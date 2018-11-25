import os
import json
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User, Group

# Create your models here.

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

ANSWER_CHOICES = (
    ('Y', 'YES'),
    ('N', 'NO'),
)

BATHROOM_CHOICES = ( 
    ('Self Contained', 'Self Contained'),
    ('Public', 'Public'),
)


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


class PropertyOwner(models.Model):
    id = models.AutoField(primary_key=True)
    # property owner(for Object level permissions)
    sys_user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=256)
    email = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Phone(models.Model):
    # Owner field Should never be blank, work on this if you get time
    # this is for the sake of create method in PropOwnerSerializer
    owner = models.ForeignKey(
        PropertyOwner, 
        on_delete=models.CASCADE, 
        related_name="phones", 
        blank=True, 
    )
    number = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.number


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
    price = models.FloatField()
    price_negotiation = models.CharField(max_length=5, blank=True, choices=ANSWER_CHOICES) 
    currency = models.CharField(max_length=256)
    descriptions = models.TextField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    owner = models.ForeignKey(PropertyOwner, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, blank=True, related_name="services")
    potentials = models.ManyToManyField(Potential, blank=True, related_name="potentials")
    post_date = models.DateTimeField(auto_now_add=True)


def img_path(instance, filename):
    ext = filename.split('.')[-1]  # get file extension
    
    if instance.pk:  # get filename
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join('property_photos', filename)


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="pictures")
    tooltip = models.CharField(max_length=256, blank=True)
    src = models.ImageField(upload_to=img_path)
    
    def delete(self, *args, **kwargs):
        img_path = settings.MEDIA_ROOT + str(self.src)
        deletion_info = super(Picture, self).delete(*args, **kwargs)
        path_exist = os.path.isfile(img_path)
        if path_exist:
            os.remove(img_path)
        return deletion_info

    def __str__(self):
        return f"{self.src}"
        
    
class Room(Property):
    width = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    length_unit = models.CharField(max_length=10, blank=True)
    area = models.FloatField(blank=True, null=True)
    bathroom = models.CharField(max_length=100, choices=BATHROOM_CHOICES, blank=True)
    tiles = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    gypsum = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    type_of_windows = models.CharField(max_length=100, blank=True)
    number_of_windows = models.SmallIntegerField(blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    electricity = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    water = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    fance = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class House(Property):
    number_of_bathrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_bedrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_livingrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_kitchens = models.SmallIntegerField(blank=True, null=True)
    number_of_store = models.SmallIntegerField(blank=True, null=True)
    tiles = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    gypsum = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    type_of_windows = models.CharField(max_length=100, blank=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    electricity = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    water = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    fance = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class Apartment(Property):
    floor_number = models.SmallIntegerField(blank=True, null=True)
    number_of_bathrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_bedrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_livingrooms = models.SmallIntegerField(blank=True, null=True)
    number_of_kitchens = models.SmallIntegerField(blank=True, null=True)
    number_of_store = models.SmallIntegerField(blank=True, null=True)
    tiles = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    gypsum = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    electricity = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    water = models.CharField(max_length=100, choices=ANSWER_CHOICES, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class Land(Property):
    width = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    length_unit = models.CharField(max_length=10, blank=True)
    area = models.FloatField(blank=True, null=True)
    is_registered = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class Frame(Property):
    width = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    length_unit = models.CharField(max_length=10, blank=True)
    area = models.FloatField(blank=True, null=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    

class Office(Property):
    width = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    length_unit = models.CharField(max_length=10, blank=True)
    area = models.FloatField(blank=True, null=True)
    floor_number = models.SmallIntegerField(blank=True, null=True)
    number_of_rooms = models.SmallIntegerField(blank=True, null=True)
    airconditioning = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    generator = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    sucurity = models.CharField(max_length=10, choices=ANSWER_CHOICES, blank=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    elevator = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    water = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class Hostel(Property):
    carrying_capacity = models.IntegerField(blank=True, null=True)
    bed_type = models.CharField(max_length=100)
    electricity = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    allow_cooking = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    tables = models.SmallIntegerField(blank=True, null=True)
    chairs = models.SmallIntegerField(blank=True, null=True)
    water = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    water_tanks = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    transport = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    generator = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    sucurity = models.CharField(max_length=10, choices=ANSWER_CHOICES, blank=True)
    payment_terms = models.SmallIntegerField(blank=True, null=True)
    unit_of_payment_terms = models.CharField(max_length=100, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    

class Hall(Property):
    area = models.FloatField(blank=True, null=True)
    area_unit = models.CharField(max_length=10, blank=True)
    carrying_capacity = models.IntegerField(blank=True, null=True)
    electricity = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    water = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    generator = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)
    parking_space = models.CharField(max_length=5, choices=ANSWER_CHOICES, blank=True)


class Feature(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='other_features')
    name = models.CharField(max_length=256, blank=True)
    value = models.CharField(max_length=256, blank=True)

