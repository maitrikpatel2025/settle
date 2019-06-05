import json
import collections

import dictfier
import django_filters
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import (
    Location, PropertyOwner, Phone, Service, Potential, Property, Feature,
    PropertyFeature, Picture, Room, House, Apartment, Hostel, Frame, Land,
    Hall, Office, Amenity
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'url', 'name')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            'id', 'url', 'country', 'region', 'distric',
            'street1', 'street2', 'longitude', 'latitude'
        )


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('url', 'owner', 'number')


class PropertyOwnerSerializer(serializers.ModelSerializer):
    phones = PhoneSerializer(many=True, read_only=False)
    class Meta:
        model = PropertyOwner
        fields = ('id', 'url', 'name', 'email', 'phones')

    def create(self, validated_data):
        phones = validated_data.pop('phones')
        owner = PropertyOwner.objects.create(**validated_data)
        owner.phones.set([
            Phone.objects.create(owner=owner, number= phone["number"])
            for phone in phones
        ])
        return owner


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'url', 'name')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'url', 'name')


class PotentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Potential
        fields = ('id', 'url', 'name')


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('id', 'url', 'is_main', 'property', 'tooltip', 'src')


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'url', 'name')

class PropertyFeatureSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(many=False, read_only=False)
    class Meta:
        model = PropertyFeature
        fields = ('id', 'url', 'property', 'feature', 'value')


class PropertySerializer(serializers.ModelSerializer):
    pictures = PictureSerializer(many=True, read_only=True)
    location = LocationSerializer(many=False, read_only=False)
    amenities = AmenitySerializer(many=True, read_only=False)
    services = ServiceSerializer(many=True, read_only=False)
    potentials = PotentialSerializer(many=True, read_only=False)
    owner = PropertyOwnerSerializer(many=False, read_only=False)
    other_features = PropertyFeatureSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = (
            'id', 'url', 'category', 'price', 'price_negotiation', 'rating',
            'currency', 'descriptions', 'location', 'owner', 'amenities',
            'services', 'potentials', 'pictures', 'other_features',
            'post_date'
        )

    def create(self, validated_data):
        """function for creating property """
        request = self.context.get('request')
        user = request.user
        location = validated_data.pop('location')
        owner = validated_data.pop('owner')
        phones = owner.pop('phones')
        amenities = validated_data.pop('amenities')
        services = validated_data.pop('services')
        potentials = validated_data.pop('potentials')

        location = Location.objects.create(**location)
        owner = PropertyOwner.objects.create(sys_user=user, **owner)
        owner.phones.set([
            Phone.objects.create(owner=owner, number= phone["number"])
            for phone in phones
        ])

        instance = type(self).Meta.model
        property = instance.objects.create(
            location=location,
            owner=owner,
            **validated_data
        )
        property.amenities.set([
            Amenity.objects.create(name=amenity["name"])
            for amenity in amenities
        ])
        property.services.set([
            Service.objects.create(name=service["name"])
            for service in services
        ])
        property.potentials.set([
            Potential.objects.create(name=potential["name"])
            for potential in potentials
        ])
        return property


class RoomSerializer(PropertySerializer):
    class Meta:
        model = Room
        fields = (
            'payment_terms', 'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class HouseSerializer(PropertySerializer):
    class Meta:
        model = House
        fields = (
            'payment_terms', 'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class ApartmentSerializer(PropertySerializer):
    class Meta:
        model = Apartment
        fields = (
            'payment_terms', 'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class LandSerializer(PropertySerializer):
    class Meta:
        model = Land
        fields = (
            'width', 'length', 'length_unit', 'area', 'is_registered',
            'payment_terms', 'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class FrameSerializer(PropertySerializer):
    class Meta:
        model = Frame
        fields = (
            'width', 'length', 'length_unit', 'area', 'payment_terms',
            'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class OfficeSerializer(PropertySerializer):
    class Meta:
        model = Office
        fields = (
            'width', 'length', 'length_unit', 'area', 'payment_terms',
            'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class HostelSerializer(PropertySerializer):
    class Meta:
        model = Hostel
        fields = ()

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class HallSerializer(PropertySerializer):
    class Meta:
        model = Hall
        fields = (
            'area', 'area_unit', 'carrying_capacity',
            'payment_terms', 'unit_of_payment_terms',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields
