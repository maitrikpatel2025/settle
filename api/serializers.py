from rest_framework import serializers
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django_restql.mixins import DynamicFieldsMixin
from django_restql.fields import NestedField
from django_restql.serializers import NestedModelSerializer

from .models import (
    Location, Contact, Service, Potential, Property, Feature,
    PropertyPicture, SingleRoom, House, Apartment, Hostel, Frame, Land,
    Office, Amenity, User, ProfilePicture, RoomType, Room
)


class ProfilePictureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ('id', 'url', 'src')

    def create(self, validated_data):
        """function for creating a profile picture """
        request = self.context.get('request')
        user = request.user

        validated_data.update({"owner": user})
        picture = super().create(validated_data)
        return picture


class MinimalPropertySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('id',)


class UserSerializer(DynamicFieldsMixin, NestedModelSerializer):
    picture = ProfilePictureSerializer(read_only=True)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    fav_properties = NestedField(
        MinimalPropertySerializer,
        many=True,
        return_pk=True,
        create_ops=[],
        update_ops=['add', 'remove'],
        required=False
    )
    
    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'email', 'password', 'phone', 'groups',
            'date_joined', 'is_staff', 'full_name', 'is_active', 'picture',
            'biography', 'fav_properties'
        )
        read_only_fields = (
            'date_joined', 'is_staff'
        )
        

class GroupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'url', 'name')


class LocationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            'id', 'url', 'address', 'point', 'latitude',
            'longitude', 'srid'
        )

        read_only_fields = (
            'longitude', 'latitude', 'srid'
        )


class ContactSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'url', 'name', 'email', 'phone')


class AmenitySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('id', 'url', 'name')


class ServiceSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'url', 'name')


class PotentialSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Potential
        fields = ('id', 'url', 'name')


class PropertyPictureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = PropertyPicture
        fields = ('id', 'url', 'is_main', 'property', 'tooltip', 'src')

    def create(self, validated_data):
        """function for creating a property picture """
        request = self.context.get('request')
        user = request.user

        property = validated_data.get("property", None)

        if property.owner != user:
            raise serializers.ValidationError(
                {"property": f"You don't own a property with `id={property.pk}`"},
                "Value error"
            )

        return super().create(validated_data)


class FeatureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'url', 'property', 'name', 'value')


class PropertySerializer(DynamicFieldsMixin, NestedModelSerializer):
    pictures = PropertyPictureSerializer(many=True, read_only=True)
    location = NestedField(LocationSerializer, many=False)
    amenities = NestedField(AmenitySerializer, many=True, required=False)
    services = NestedField(ServiceSerializer, many=True, required=False)
    potentials = NestedField(PotentialSerializer, many=True, required=False)
    contact = NestedField(ContactSerializer, many=False, required=False)
    other_features = NestedField(FeatureSerializer,
        many=True, required=False, create_ops=["create"],
        update_ops=["update", "create", "remove"]
    )
    owner = UserSerializer(many=False, read_only=True, exclude=['fav_properties'])
    is_my_favourite = serializers.SerializerMethodField()
    type = serializers.CharField(read_only=True)

    # This is used when retrieving nearby properties
    distance = serializers.CharField(default=None)

    class Meta:
        model = Property
        fields = (
            'id', 'url', 'type', 'available_for', 'available_for_options', 'price',
            'price_rate_unit', 'payment_terms', 'is_price_negotiable', 'rating',
            'currency', 'descriptions', 'location', 'owner', 'amenities',
            'services', 'potentials', 'pictures', 'other_features', 'contact',
            'post_date', 'is_my_favourite', 'distance'
        )
        
    def get_is_my_favourite(self, obj):
        request = self.context.get('request')
        user = request.user
        
        if user.is_authenticated:
            return user.fav_properties.all().filter(id=obj.id).exists()
        return False

    def create(self, validated_data):
        """function for creating a property """
        request = self.context.get('request')
        user = request.user

        validated_data.update({"owner": user})
        property = super().create(validated_data)
        return property


class RoomTypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ('id', 'url', 'code', 'name', 'descriptions')


class RoomSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'url', 'property', 'type', 'count')


class SingleRoomSerializer(PropertySerializer):
    rooms = NestedField(RoomSerializer, many=True, required=False)
    class Meta:
        model = SingleRoom
        fields = ('rooms',)

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class HouseSerializer(PropertySerializer):
    rooms = NestedField(RoomSerializer, many=True, required=False)
    class Meta:
        model = House
        fields = ('rooms',)

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class ApartmentSerializer(PropertySerializer):
    rooms = NestedField(RoomSerializer, many=True, required=False)
    class Meta:
        model = Apartment
        fields = ('rooms',)

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class LandSerializer(PropertySerializer):
    class Meta:
        model = Land
        fields = (
            'width', 'length', 'area', 'is_registered',
        )

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class FrameSerializer(PropertySerializer):
    class Meta:
        model = Frame
        fields = ()

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class OfficeSerializer(PropertySerializer):
    class Meta:
        model = Office
        fields = ()

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class HostelSerializer(PropertySerializer):
    rooms = NestedField(RoomSerializer, many=True, required=False)
    class Meta:
        model = Hostel
        fields = ('rooms',)

    Meta.fields = PropertySerializer.Meta.fields + Meta.fields


class NearbyLocationSerializer(serializers.Serializer):
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)
    radius_to_scan = serializers.FloatField(required=True)
