from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import (
    Location, Contact, Service, Potential, Property, Feature,
    Picture, Room, House, Apartment, Hostel, Frame, Land,
    Hall, Office, Amenity
)


class PrettyUpdate(object):
    def constrain_error_prefix(self, field):
        return f"Error on {field} field: "

    def update_related_field(self, instance, field, value):
        try:
            setattr(instance, field+"_id", value)
        except Exception as e:
            message = self.constrain_error_prefix(field) + str(e)
            raise serializers.ValidationError(message)

    def update_many_to_many_ralated_field(self, instance, field, value):
        if isinstance(value, dict):
            obj = getattr(instance, field)
            for operator in value:
                if operator == "add":
                    try:
                        obj.add(*value[operator])
                    except Exception as e:
                        message = self.constrain_error_prefix(field) + str(e)
                        raise serializers.ValidationError(message)
                elif operator == "remove":
                    try:
                        obj.remove(*value[operator])
                    except Exception as e:
                        message = self.constrain_error_prefix(field) + str(e)
                        raise serializers.ValidationError(message)
                else:
                    message = (
                        f"{operator} is an invalid operator, "
                        "allowed operators are 'add' and 'remove'"
                    )
                    raise serializers.ValidationError(message)
        elif isinstance(value, list):
            try:
                getattr(instance, field).set(value)
            except Exception as e:
                message = self.constrain_error_prefix(field) + str(e)
                raise serializers.ValidationError(message)
        else:
            message = (
                f"{field} value must be of type list or dict "
                f"and not {type(value).__name__}"
            )
            raise serializers.ValidationError(message)

    def update_one_to_many_ralated_field(self, instance, field, value):
        if isinstance(value, dict):
            obj = getattr(instance, field)
            for operator in value:
                if operator == "delete":
                    try:
                        obj.filter(pk__in=value[operator]).delete()
                    except Exception as e:
                        message = self.constrain_error_prefix(field) + str(e)
                        raise serializers.ValidationError(message)
                else:
                    message = (
                        f"{operator} is an invalid operator, "
                        "allowed operators are 'add' and 'delete'"
                    )
                    raise serializers.ValidationError(message)
        elif isinstance(value, list):
            try:
                getattr(instance, field).set(value)
            except Exception as e:
                message = self.constrain_error_prefix(field) + str(e)
                raise serializers.ValidationError(message)
        else:
            message = (
                f"{field} value must be of type list or dict "
                f"and not {type(value).__name__}"
            )
            raise serializers.ValidationError(message)

    def pretty_update(self, instance, data):
        for field in data:
            field_type = self.get_fields()[field]
            if isinstance(field_type, serializers.Serializer):
                self.update_related_field(instance, field, data[field])
            elif isinstance(field_type, serializers.ListSerializer):
                relation = getattr(instance, field).__class__.__name__
                if relation == "ManyRelatedManager":
                    self.update_many_to_many_ralated_field(instance, field, data[field])
                if relation == "RelatedManager":
                    self.update_one_to_many_ralated_field(instance, field, data[field])
            else:
                pass

    def update(self, instance, validated_data):
        """Pretty update """
        request = self.context.get('request')
        data = request.data
        self.pretty_update(instance, data)
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            message = str(e)
            raise serializers.ValidationError(e)


class UserSerializer(PrettyUpdate, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'password', 'groups')

    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_user(username, email, password)
        return user

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


class ContactSerializer(PrettyUpdate, serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'url', 'name', 'email', 'phone')


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
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


class FeatureSerializer(PrettyUpdate, serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'url', 'property', 'name', 'value')


class PropertySerializer(PrettyUpdate, serializers.ModelSerializer):
    pictures = PictureSerializer(many=True, read_only=True)
    location = LocationSerializer(many=False, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    potentials = PotentialSerializer(many=True, read_only=True)
    contact = ContactSerializer(many=False, read_only=True)
    other_features = FeatureSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = (
            'id', 'url', 'category', 'price', 'price_negotiation', 'rating',
            'currency', 'descriptions', 'location', 'owner', 'amenities',
            'services', 'potentials', 'pictures', 'other_features', 'contact',
            'post_date', 'prop_type'
        )

    def create(self, validated_data):
        """function for creating property """
        request = self.context.get('request')
        prop_type = request.path.strip().split("/")[-2]
        user = request.user
        data = request.data
        location = data.pop('location')
        contact = data.pop('contact')
        amenities = data.pop('amenities', None)
        services = data.pop('services', None)
        potentials = data.pop('potentials', None)
        other_features = data.pop('other_features', None)

        location = Location.objects.create(**location)
        contact = Contact.objects.create(**contact)

        instance = type(self).Meta.model
        property = instance.objects.create(
            location=location,
            owner=user,
            contact=contact,
            prop_type=prop_type,
            **validated_data
        )

        if amenities is not None:
            property.amenities.set(amenities)

        if services is not None:
            property.services.set(services)

        if potentials is not None:
            property.potentials.set(potentials)

        if other_features is not None:
            for other_feature in other_features:
                Feature.objects.create(
                    property=property, 
                    **other_feature
                )

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
