import django_filters
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Location, PropertyOwner, Phone, Service, Potential, Property, Feature,
    Picture, Room, House, Apartment, Hostel, Frame, Land, Hall, Office
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class PropertyOwnerSerializer(serializers.ModelSerializer):
    phones = PhoneSerializer(many=True, read_only=False)
    class Meta:
        model = PropertyOwner
        fields = ('id', 'url', 'name', 'email', 'phones')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def create(self, validated_data):
        phones = validated_data.pop('phones')
        owner = PropertyOwner.objects.create(**validated_data)
        owner.phones.set([
            Phone.objects.create(owner=owner, number= phone["number"]) 
            for phone in phones
        ])
        return owner


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
        fields = ('id', 'url', 'property', 'tooltip', 'src')


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'url', 'property', 'name', 'value')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class PropertySerializer(serializers.ModelSerializer):
    pictures = PictureSerializer(many=True, read_only=True)
    location = LocationSerializer(many=False, read_only=False)
    services = ServiceSerializer(many=True, read_only=False)
    potentials = PotentialSerializer(many=True, read_only=False)
    owner = PropertyOwnerSerializer(many=False, read_only=False)
    other_features = FeatureSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'pictures', 'other_features'
        )

    def create(self, validated_data):
        """function for creating property """
        request = self.context.get('request')
        user = request.user
        location = validated_data.pop('location')
        owner = validated_data.pop('owner')
        phones = owner.pop('phones')
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
        property.services.set([
            Service.objects.create(name=service["name"]) 
            for service in services
        ])
        property.potentials.set([
            Potential.objects.create(name=potential["name"]) 
            for potential in potentials
        ])
        return property

    def to_representation(self, instance):
        data = super().to_representation(instance)
        #request = self.context.get('request')
        #put your custom code here
        #data['potentials'] = 
        #[potential.name for potential in instance.potentials.all()]
        return data


class RoomSerializer(PropertySerializer):
    class Meta:
        model = Room
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'width', 'length', 'length_unit',
            'area', 'bathroom', 'tiles', 'gypsum', 'type_of_windows',
            'number_of_windows', 'payment_terms', 'unit_of_payment_terms',
            'electricity', 'water', 'fance', 'parking_space', 'post_date',
            'pictures', 'other_features'
        )


class HouseSerializer(PropertySerializer):
    class Meta:
        model = House
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'number_of_bathrooms', 'number_of_bedrooms',
            'number_of_livingrooms', 'number_of_kitchens',
            'number_of_store', 'tiles', 'gypsum', 'type_of_windows',
            'payment_terms', 'unit_of_payment_terms', 'electricity',
            'water', 'fance', 'parking_space', 'post_date', 'pictures',
            'other_features'
        )


class ApartmentSerializer(PropertySerializer):
    class Meta:
        model = Apartment
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'floor_number', 'number_of_bathrooms',
            'number_of_bedrooms', 'number_of_livingrooms',
            'number_of_kitchens', 'number_of_store', 'tiles',
            'gypsum', 'payment_terms', 'unit_of_payment_terms',
            'electricity', 'water', 'parking_space', 'post_date',
            'pictures', 'other_features'

        )


class LandSerializer(PropertySerializer):
    class Meta:
        model = Land
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'width', 'length', 'length_unit',
            'area', 'is_registered', 'post_date', 'pictures',
            'other_features'
        )


class FrameSerializer(PropertySerializer):
    class Meta:
        model = Frame
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'width', 'length', 'length_unit',
            'area', 'payment_terms', 'unit_of_payment_terms',
            'post_date', 'pictures', 'other_features'
        )


class OfficeSerializer(PropertySerializer):
    class Meta:
        model = Office
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'width', 'length', 'length_unit',
            'area', 'floor_number', 'number_of_rooms',
            'airconditioning', 'generator', 'sucurity', 'payment_terms',
            'unit_of_payment_terms', 'parking_space', 'elevator',
            'water', 'post_date', 'pictures', 'other_features'
        )


class HostelSerializer(PropertySerializer):
    class Meta:
        model = Hostel
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'carrying_capacity', 'bed_type',
            'electricity', 'allow_cooking', 'tables', 'chairs',
            'water', 'water_tanks', 'transport', 'generator',
            'sucurity', 'payment_terms', 'unit_of_payment_terms',
            'parking_space', 'post_date', 'pictures', 'other_features'
        )


class HallSerializer(PropertySerializer):
    class Meta:
        model = Hall
        fields = (
            'id', 'url', 'price', 'price_negotiation', 'currency',
            'descriptions', 'location', 'owner', 'services',
            'potentials', 'area', 'area_unit', 'carrying_capacity',
            'electricity', 'water', 'generator', 'parking_space',
            'pictures', 'other_features'
        )


