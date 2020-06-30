import os
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

AVAILABLE_FOR_CHOICES = (
    ('sale', 'Sale'),
    ('rent', 'Rent'),
)

ANSWER_CHOICES = (
    ('Y', 'YES'),
    ('N', 'NO'),
)


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
    country = models.CharField(max_length=256, blank=True)
    region = models.CharField(max_length=256, blank=True)
    distric = models.CharField(max_length=256, blank=True)
    street1 = models.CharField(max_length=256, blank=True)
    street2 = models.CharField(max_length=256, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.country}, {self.region}, {self.distric}, {self.street1}, {self.street2}"


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
    type = models.CharField(max_length=256, editable=False, default="generic")
    available_for = models.CharField(max_length=5, choices=AVAILABLE_FOR_CHOICES)
    price = models.FloatField()
    currency = models.CharField(max_length=256)
    price_negotiation = models.CharField(max_length=5, blank=True, null=True, choices=ANSWER_CHOICES)
    descriptions = models.TextField(blank=True, null=True)
    rating = models.SmallIntegerField(default=3, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.CASCADE)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="properties")
    services = models.ManyToManyField(Service, blank=True, related_name="properties")
    potentials = models.ManyToManyField(Potential, blank=True, related_name="properties")
    post_date = models.DateTimeField(auto_now_add=True)
    
    def available_for_options(self):
        return []

    def __str__(self):
        return (
            "%s, %s, %s, %s, %s, %s" %
            (
                self.__class__.__name__,
                self.location.country,
                self.location.region,
                self.location.distric,
                self.location.street1,
                self.location.street2
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


class Room(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent']
        
    def save(self, *args, **kwargs):
        self.type = "room"
        super().save(*args, **kwargs)


class House(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent', 'sale']
        
    def save(self, *args, **kwargs):
        self.type = "house"
        super().save(*args, **kwargs)


class Apartment(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent', 'sale']
        
    def save(self, *args, **kwargs):
        self.type = "apartment"
        super().save(*args, **kwargs)


class Land(Property):
    width = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    length_unit = models.CharField(max_length=10, blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    is_registered = models.CharField(max_length=5, blank=True, null=True, choices=ANSWER_CHOICES)

    def available_for_options(self):
        return ['sale']
        
    def save(self, *args, **kwargs):
        self.type = "land"
        super().save(*args, **kwargs)


class Frame(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent']
        
    def save(self, *args, **kwargs):
        self.type = "frame"
        super().save(*args, **kwargs)


class Office(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent']
        
    def save(self, *args, **kwargs):
        self.type = "office"
        super().save(*args, **kwargs)


class Hostel(Property):
    price_rate_unit = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    payment_terms_unit = models.CharField(max_length=100, blank=True, null=True)

    def available_for_options(self):
        return ['rent']
        
    def save(self, *args, **kwargs):
        self.type = "hostel"
        super().save(*args, **kwargs)


class Feature(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='other_features')
    name = models.CharField(max_length=256, blank=True, null=True)
    value = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.name
