import os
from uuid import uuid4

from django.db.models import Q, Sum
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Property availability
SALE = 'sale'
RENT = 'rent'

AVAILABILITY_CHOICES = (
    (SALE, 'Sale'),
    (RENT, 'Rent'),
)

ANSWER_CHOICES = (
    ('Y', 'YES'),
    ('N', 'NO'),
)

# Property types
PROPERTY = 'generic'
ROOM = 'room'
HOUSE = 'house'
APARTMENT = 'apartment'
LAND = 'land'
FRAME = 'frame'
OFFICE = 'office'
HOSTEL = 'hostel'

# Property type => availability
PROPERTIES_AVAILABILITY = {
    PROPERTY: [],
    ROOM: [RENT],
    HOUSE: [RENT, SALE],
    APARTMENT: [RENT, SALE],
    LAND: [SALE],
    FRAME: [RENT],
    OFFICE: [RENT],
    HOSTEL: [RENT]
}


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def profile_picture_path(instance, filename):
    ext = filename.split('.')[-1]  # Get file extension

    if instance.pk:  # Get filename
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join('profile_pictures', filename)


class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    biography = models.TextField(max_length=256, blank=True)
    fav_properties = models.ManyToManyField('Property')


class ProfilePicture(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="picture")
    src = models.ImageField(upload_to=profile_picture_path)

    def delete(self, *args, **kwargs):
        img_path = settings.MEDIA_ROOT + str(self.src)
        deletion_info = super(ProfilePicture, self).delete(*args, **kwargs)
        path_exist = os.path.isfile(img_path)
        if path_exist:
            os.remove(img_path)
        return deletion_info

    def __str__(self):
        return f"{self.src}"


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.PointField(default=Point(0.0, 0.0))
    address = models.CharField(max_length=256, blank=True)

    @property
    def longitude(self):
        return self.point.x

    @property
    def latitude(self):
        return self.point.y

    @property
    def srid(self):
        return self.point.srid

    def __str__(self):
        return f"{self.address}"


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    phone = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Potential(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Property(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=256, editable=False, default=PROPERTY)
    available_for = models.CharField(max_length=5, choices=AVAILABILITY_CHOICES)
    price = models.FloatField()
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=256)
    payment_terms = models.TextField(blank=True, null=True)
    is_price_negotiable = models.CharField(max_length=5, blank=True, null=True, choices=ANSWER_CHOICES)
    descriptions = models.TextField(blank=True, null=True)
    rating = models.SmallIntegerField(default=3, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, blank=True, null=True, on_delete=models.CASCADE)
    contact = models.OneToOneField(Contact, blank=True, null=True, on_delete=models.CASCADE)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")
    services = models.ManyToManyField(Service, blank=True, related_name="properties")
    potentials = models.ManyToManyField(Potential, blank=True, related_name="properties")
    post_date = models.DateTimeField(auto_now_add=True)
    
    def available_for_options(self):
        return []
        
    def __str__(self):
        return (
            "%s, %s" %
            (
                self.__class__.__name__,
                self.location.address
            )
        )


def property_img_path(instance, filename):
    ext = filename.split('.')[-1]  # Get file extension

    if instance.pk:  # Get filename
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join('property_photos', filename)


class PropertyPicture(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="pictures")
    is_main = models.BooleanField(default=False)
    tooltip = models.CharField(max_length=256, blank=True)
    src = models.ImageField(upload_to=property_img_path)

    def delete(self, *args, **kwargs):
        img_path = settings.MEDIA_ROOT + str(self.src)
        deletion_info = super(PropertyPicture, self).delete(*args, **kwargs)
        path_exist = os.path.isfile(img_path)
        if path_exist:
            os.remove(img_path)
        return deletion_info

    def __str__(self):
        return f"{self.src}"


class RoomsCountMixin():
    def rooms_count(self):
        return self.rooms.get_queryset().filter(
            ~ Q(type__code__in=['BAR_PU', 'BAR_PR', 'BAR_MA'])
        ).aggregate(Sum('count'))['count__sum'] or 0


class SingleRoom(RoomsCountMixin, Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[ROOM]

    def save(self, *args, **kwargs):
        self.type = ROOM
        super().save(*args, **kwargs)


class House(RoomsCountMixin, Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[HOUSE]
        
    def save(self, *args, **kwargs):
        self.type = HOUSE
        super().save(*args, **kwargs)


class Apartment(RoomsCountMixin, Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[APARTMENT]
        
    def save(self, *args, **kwargs):
        self.type = APARTMENT
        super().save(*args, **kwargs)


class Land(Property):
    square_meters = models.FloatField()
    is_registered = models.CharField(max_length=5, blank=True, null=True, choices=ANSWER_CHOICES)

    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[LAND]
        
    def save(self, *args, **kwargs):
        self.type = LAND
        super().save(*args, **kwargs)


class Frame(Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[FRAME]
        
    def save(self, *args, **kwargs):
        self.type = FRAME
        super().save(*args, **kwargs)


class Office(Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[OFFICE]
        
    def save(self, *args, **kwargs):
        self.type = OFFICE
        super().save(*args, **kwargs)


class Hostel(RoomsCountMixin, Property):
    def available_for_options(self):
        return PROPERTIES_AVAILABILITY[HOSTEL]
        
    def save(self, *args, **kwargs):
        self.type = HOSTEL
        super().save(*args, **kwargs)


class Feature(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='other_features')
    name = models.CharField(max_length=256, blank=True, null=True)
    value = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=256)
    descriptions = models.TextField(blank=True, null=True)


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    type = models.OneToOneField(RoomType, on_delete=models.CASCADE)
    count = models.IntegerField()

    class Meta:
        unique_together = ('property', 'type')
