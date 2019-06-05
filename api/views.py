import json
import itertools

from django.db.models import Value
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from django_restql.mixins import DynamicFieldsMixin
from django.db.models.functions import Concat, Replace
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from api.permissions import IsOwnerOrReadOnly, IsAllowedUser
from .models import (
    Location, PropertyOwner, Phone, Service, Potential, Property, Picture,
    Room, House, Apartment, Hostel, Frame, Land, Hall, Office, Feature,
    PropertyFeature, Amenity
)
from .serializers import (
    UserSerializer, GroupSerializer, LocationSerializer, FeatureSerializer,
    PropertyOwnerSerializer, PhoneSerializer, ServiceSerializer,
    PotentialSerializer, PropertySerializer, PictureSerializer,
    RoomSerializer, HouseSerializer, ApartmentSerializer, HostelSerializer,
    FrameSerializer, LandSerializer, HallSerializer, OfficeSerializer,
    AmenitySerializer, PropertyFeatureSerializer
)


def fields(*args):
    """ Specify the field lookup that should be performed in a filter call.
    Default lookup is exact.
    """
    lookup_fields = {}
    for field in args:
        if isinstance(field, str):
            lookup_fields.update({field: ['exact']})
        elif isinstance(field, dict):
            lookup_fields.update(field)
        else:
            raise Exception("Invalid formating of lookup field")

    return lookup_fields


class UserViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAllowedUser)
    filter_fields = fields(
        'id', {'email': ['exact', 'icontains']},
        'groups', {'username': ['exact', 'icontains']}
    )


class GroupViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows groups to be viewed or edited."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAllowedUser)
    filter_fields = fields('id', 'name')


class LocationViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Location to be viewed or edited."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'country', 'region', 'distric', 'street1',
        'street2', 'longitude', 'latitude'
    )


class PropertyOwnerViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows PropertyOwner to be viewed or edited."""
    queryset = PropertyOwner.objects.all()
    serializer_class = PropertyOwnerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'name', {'email': ['exact', 'icontains']},
        'phones',
    )


class PhoneViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Phone to be viewed or edited."""
    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('owner', 'number')


class AmenityViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Amenity to be viewed or edited."""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'name')


class ServiceViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Service to be viewed or edited."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'name')


class PotentialViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Potential to be viewed or edited."""
    queryset = Potential.objects.all()
    serializer_class = PotentialSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'name')


class PropertyViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Property to be viewed or edited."""
    queryset = Property.objects.all().order_by('-post_date')
    serializer_class = PropertySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_fields = fields(
        'id',  'category', {'price': ['exact', 'lt', 'gt']},
        'price_negotiation', 'currency', 'location', 'owner',
        {'post_date': ['exact', 'lt', 'gt', 'range']},
    )

    def destroy(self, request, pk=None):
        """Function for deleting property and its associated components"""
        property = self.queryset.get(pk=pk)
        location = property.location
        owner = property.owner
        phones = owner.phones
        services = property.services
        potentials = property.potentials
        pictures = property.pictures
        other_features = property.other_features
        phones.get_queryset().delete()
        services.get_queryset().delete()
        potentials.get_queryset().delete()

        # Don't use bulk deletion because it doesn't use overriden delete
        # on Picture Model, so with it picture files won't be deleted
        for picture in pictures.get_queryset():
            picture.delete()

        other_features.get_queryset().delete()
        property.delete()
        owner.delete()
        location.delete()

    def contains_lookup(self, request, queryset, field):
        if request.GET.get(field) is not None:
            value = json.loads(request.GET[field])
            field = field.replace("__contains", "__in")
            lookup = {field: value}
            for field in value:
                queryset = queryset.filter(**lookup)
        return queryset

    def location_lookup(self, request, queryset, field):
        # If there is no location(loc) parameter on request params
        if request.GET.get(field) is not None:
            keyword = request.GET[field].replace(' ', '').replace(',', '')
            queryset = queryset.annotate(full_location=Replace(Concat(
                'location__country',
                'location__region',
                'location__distric',
                'location__street1',
                'location__street2'
            ), Value(' '), Value(''))).filter(full_location__icontains=keyword)
        return queryset

    def filter_queryset(self, queryset):
        """Do a custom search of location in every field of Location model"""
        request = self.request
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        queryset = self.location_lookup(request, queryset, "loc")
        queryset = self.contains_lookup(request, queryset, "services__contains")
        queryset = self.contains_lookup(request, queryset, "amenities__contains")
        queryset = self.contains_lookup(request, queryset, "potentials__contains")
        return queryset


class PictureViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Picture to be viewed or edited."""
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer
    filter_fields = fields('id', 'property', 'tooltip')


class RoomViewSet(PropertyViewSet):
    """API endpoint that allows Room to be viewed or edited."""
    queryset = Room.objects.all().order_by('-post_date')
    serializer_class = RoomSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class HouseViewSet(PropertyViewSet):
    """API endpoint that allows House to be viewed or edited."""
    queryset = House.objects.all().order_by('-post_date')
    serializer_class = HouseSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}

class ApartmentViewSet(PropertyViewSet):
    """API endpoint that allows Apartment to be viewed or edited."""
    queryset = Apartment.objects.all().order_by('-post_date')
    serializer_class = ApartmentSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}

class LandViewSet(PropertyViewSet):
    """API endpoint that allows Land to be viewed or edited."""
    queryset = Land.objects.all().order_by('-post_date')
    serializer_class = LandSerializer
    filter_fields = fields()
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class FrameViewSet(PropertyViewSet):
    """API endpoint that allows Frame to be viewed or edited."""
    queryset = Frame.objects.all().order_by('-post_date')
    serializer_class = FrameSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class OfficeViewSet(PropertyViewSet):
    """API endpoint that allows Office to be viewed or edited."""
    queryset = Office.objects.all().order_by('-post_date')
    serializer_class = OfficeSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}

class HostelViewSet(PropertyViewSet):
    """API endpoint that allows Hostel to be viewed or edited."""
    queryset = Hostel.objects.all().order_by('-post_date')
    serializer_class = HostelSerializer
    filter_fields = fields(
        'unit_of_payment_terms', {'payment_terms': ['exact', 'lt', 'gt']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class HallViewSet(PropertyViewSet):
    """API endpoint that allows Hall to be viewed or edited."""
    queryset = Hall.objects.all().order_by('-post_date')
    serializer_class = HallSerializer
    filter_fields = fields()
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class FeatureViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Feature to be viewed or edited."""
    queryset = Feature.objects.all().order_by('-name')
    serializer_class = FeatureSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'name')


class PropertyFeatureViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """API endpoint that allows PropertyFeature to be viewed or edited."""
    queryset = PropertyFeature.objects.all().order_by('-id')
    serializer_class = PropertyFeatureSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'property', 'value')
