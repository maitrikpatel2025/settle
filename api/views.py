import itertools
from django.db.models import Value
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from django.db.models.functions import Concat, Replace
from .models import (
    Location, PropertyOwner, Phone, Service, Potential, Property, Picture, 
    Room, House, Apartment, Hostel, Frame, Land, Hall, Office, Feature
)
from .serializers import (
    UserSerializer, GroupSerializer, LocationSerializer, FeatureSerializer,
    PropertyOwnerSerializer, PhoneSerializer, ServiceSerializer,
    PotentialSerializer, PropertySerializer, PictureSerializer,
    RoomSerializer, HouseSerializer, ApartmentSerializer, HostelSerializer,
    FrameSerializer, LandSerializer, HallSerializer, OfficeSerializer
)


def fields(*args):
    """ Specify the field lookup that should be performed in a filter call.
    Default lookup is exact.
    """
    default_lookup_fields = filter(lambda field: isinstance(field, str), args)
    custom_lookup_fields = filter(lambda field: isinstance(field, dict), args)
    default_lookup_fields = {
        key: value 
        for key, value in 
        itertools.zip_longest(default_lookup_fields, [], fillvalue=['exact'])
    } 
    custom_lookup_fields = {
        key: value 
        for dic in 
        custom_lookup_fields 
        for key, value in dic.items()
    }
    return {**default_lookup_fields, **custom_lookup_fields}


def custom_filtered_queryset(view, queryset):
    """Do a custom search of location in every field of Location model"""
    request = view.request
    for backend in list(view.filter_backends):
        queryset = backend().filter_queryset(request, queryset, view)

    if request.GET.get('loc') is None:
        return queryset  #if there is no location(loc) parameter in request
        
    keyword = request.GET['loc'].replace(' ', '').replace(',', '')
    queryset = queryset.annotate(full_location=Replace(Concat(
        'location__country', 
        'location__region', 
        'location__distric', 
        'location__street1',
        'location__street2'
        ), Value(' '), Value(''))).filter(full_location__icontains=keyword)
    return queryset


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_fields = fields(
        'id', {'email': ['exact', 'icontains']}, 
        'groups', {'username': ['exact', 'icontains']}
    )


class GroupViewSet(viewsets.ModelViewSet):
    """API endpoint that allows groups to be viewed or edited."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_fields = fields('id', 'name')


class LocationViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Location to be viewed or edited."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_fields = fields(
        'id', 'country', 'region', 'distric', 'street1', 
        'street2', 'longitude', 'latitude'
    )


class PropertyOwnerViewSet(viewsets.ModelViewSet):
    """API endpoint that allows PropertyOwner to be viewed or edited."""
    queryset = PropertyOwner.objects.all()
    serializer_class = PropertyOwnerSerializer
    filter_fields = fields(
        'id', 'name', {'email': ['exact', 'icontains']}, 
        'phones',
    )
    

class PhoneViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Phone to be viewed or edited."""
    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer
    filter_fields = fields('owner', 'number')


class ServiceViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Service to be viewed or edited."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_fields = fields('id', 'name')


class PotentialViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Potential to be viewed or edited."""
    queryset = Potential.objects.all()
    serializer_class = PotentialSerializer
    filter_fields = fields('id', 'name')


class PropertyViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Property to be viewed or edited."""
    queryset = Property.objects.all().order_by('-post_date')
    serializer_class = PropertySerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation',
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', 'pictures', 'location__street1', 
        {'post_date': ['exact', 'lt', 'gt', 'range']},
    )


class PictureViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Picture to be viewed or edited."""
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer
    filter_fields = fields('id', 'property', 'tooltip')


class RoomViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Room to be viewed or edited."""
    queryset = Room.objects.all().order_by('-post_date')
    serializer_class = RoomSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation', 
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', 'width', 'length', 'length_unit', 
        'area', 'bathroom', 'tiles', 'gypsum', 'type_of_windows', 
        'number_of_windows', {'payment_terms': ['exact', 'lt', 'gt']}, 
        'unit_of_payment_terms', 'electricity', 'water', 'fance', 
        'parking_space', {'post_date': ['exact', 'lt', 'gt', 'range']}, 
        'pictures',
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class HouseViewSet(viewsets.ModelViewSet):
    """API endpoint that allows House to be viewed or edited."""
    queryset = House.objects.all().order_by('-post_date')
    serializer_class = HouseSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation', 
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', {'number_of_bathrooms': ['exact', 'lt', 'gt']}, 
        {'number_of_bedrooms': ['exact', 'lt', 'gt']}, 'pictures',
        {'number_of_livingrooms': ['exact', 'lt', 'gt']}, 
        {'number_of_kitchens': ['exact', 'lt', 'gt']}, 
        {'number_of_store': ['exact', 'lt', 'gt']}, 'tiles', 'gypsum', 
        'type_of_windows', {'payment_terms': ['exact', 'lt', 'gt']}, 
        'unit_of_payment_terms', 'electricity', 'water', 'fance', 
        'parking_space', {'post_date': ['exact', 'lt', 'gt']},
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class ApartmentViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Apartment to be viewed or edited."""
    queryset = Apartment.objects.all().order_by('-post_date')
    serializer_class = ApartmentSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation', 
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', 'floor_number', 'gypsum', 'unit_of_payment_terms', 
        {'number_of_bathrooms': ['exact', 'lt', 'gt']}, 
        {'number_of_bedrooms': ['exact', 'lt', 'gt']}, 
        {'number_of_livingrooms': ['exact', 'lt', 'gt']}, 
        {'number_of_kitchens': ['exact', 'lt', 'gt']}, 
        {'number_of_store': ['exact', 'lt', 'gt']}, 'tiles', 
        {'payment_terms': ['exact', 'lt', 'gt']},
        'electricity', 'water', 'parking_space', 
        {'post_date': ['exact', 'lt', 'gt']},'pictures',
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class LandViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Land to be viewed or edited."""
    queryset = Land.objects.all().order_by('-post_date')
    serializer_class = LandSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation', 
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', 'width', 'length', 'length_unit', 'area', 
        'is_registered', {'post_date': ['exact', 'lt', 'gt']}, 
        'pictures'
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class FrameViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Frame to be viewed or edited."""
    queryset = Frame.objects.all().order_by('-post_date')
    serializer_class = FrameSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 
        'price_negotiation', 'currency', 'descriptions', 
        'location', 'owner', 'services', 'potentials', 
        'width', 'length', 'length_unit', 'area', 
        {'payment_terms': ['exact', 'lt', 'gt']}, 
        'unit_of_payment_terms', 'pictures',
        {'post_date': ['exact', 'lt', 'gt']},
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class OfficeViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Office to be viewed or edited."""
    queryset = Office.objects.all().order_by('-post_date')
    serializer_class = OfficeSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 
        'price_negotiation', 'currency', 
        'descriptions', 'location', 'owner', 'services', 
        'potentials', 'width', 'length', 'length_unit', 
        'area', 'floor_number', 'pictures', 'elevator', 
        {'number_of_rooms': ['exact', 'lt', 'gt']}, 
        'airconditioning', 'generator', 'sucurity', 
        {'payment_terms': ['exact', 'lt', 'gt']},
        'unit_of_payment_terms', 'parking_space', 
        'water', {'post_date': ['exact', 'lt', 'gt']},
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class HostelViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Hostel to be viewed or edited."""
    queryset = Hostel.objects.all().order_by('-post_date')
    serializer_class = HostelSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation', 
        'currency', 'descriptions', 'location', 'owner', 'services', 
        'potentials', {'carrying_capacity': ['exact', 'lt', 'gt']}, 
        'bed_type', 'electricity', 'allow_cooking', 'tables', 
        'chairs', 'water', 'water_tanks', 'transport', 'generator', 
        'sucurity', {'payment_terms': ['exact', 'lt', 'gt']}, 
        'unit_of_payment_terms', 'parking_space', 
        {'post_date': ['exact', 'lt', 'gt']}, 'pictures',
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset


class HallViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Hall to be viewed or edited."""
    queryset = Hall.objects.all().order_by('-post_date')
    serializer_class = HallSerializer
    filter_fields = fields(
        'id', {'price': ['exact', 'lt', 'gt']}, 'price_negotiation',
        'currency', 'descriptions', 'location', 'owner', 'services',
        'potentials', 'area', 'area_unit', 'pictures',
        {'carrying_capacity': ['exact', 'lt', 'gt']}, 
        'electricity', 'water', 'generator', 'parking_space',  
    )

    def filter_queryset(self, queryset):
        queryset = custom_filtered_queryset(self, queryset)
        return queryset

class FeatureViewSet(viewsets.ModelViewSet):
    """API endpoint that allows Feature to be viewed or edited."""
    queryset = Feature.objects.all().order_by('-name')
    serializer_class = FeatureSerializer
    filter_fields = fields('id', 'property', 'name', 'value')