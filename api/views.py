import json

from django.db.models import Value
from rest_framework import views, viewsets, status, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django_restql.mixins import (
    EagerLoadingMixin, QueryArgumentsMixin
)
from django.contrib.auth.models import Group
from django.db.models.functions import Concat, Replace
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
)

from api.permissions import (
    IsOwnerOrReadOnly, IsAllowedUser, HasGroupPermission, 
    BelongsToPropertyOwnedByAuthenticatedUser, IsAdminOrReadOnly
)
from .models import (
    Location, Contact, Service, Potential, Property, PropertyPicture, SingleRoom,
    House, Apartment, Hostel, Frame, Land, Office, Feature, Amenity, User,
    ProfilePicture, PROPERTIES_AVAILABILITY, RoomType
)
from .serializers import (
    UserSerializer, GroupSerializer, LocationSerializer, FeatureSerializer,
    ContactSerializer, ServiceSerializer, PotentialSerializer,
    PropertySerializer, PropertyPictureSerializer, SingleRoomSerializer, HouseSerializer,
    ApartmentSerializer, HostelSerializer, FrameSerializer, LandSerializer,
    OfficeSerializer, AmenitySerializer, ProfilePictureSerializer,
    NearbyLocationSerializer, RoomTypeSerializer
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


class AuthenticateUserViewSet(viewsets.ViewSet):
    """API endpoint that allows users to login and obtain auth token."""
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = ObtainAuthToken.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        data = {
            'token': token.key,
            **user_serializer.data
        }
        return Response(data)


class RegisterUserViewSet(viewsets.ViewSet):
    """API endpoint that allows users to register and obtain auth token."""
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = UserSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        full_name = data.pop("full_name", "")
        username = data.pop("username")
        email = data.pop("email", "")
        password = data.pop("password")
        user = User.objects.create_user(
            username, email, password,
            full_name=full_name
        )
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        data = {
            'token': token.key,
            **user_serializer.data
        }
        return Response(data)


class ProfilePictureViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Profile Picture to be viewed or edited."""
    queryset = ProfilePicture.objects.all()
    serializer_class = ProfilePictureSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    filter_fields = fields('id',)


class UserViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsAllowedUser, HasGroupPermission)
    http_method_names = ['get', 'put', 'patch', 'head', 'delete']
    filter_fields = fields(
        'id', {'email': ['exact', 'icontains']}, 'full_name',
        'groups', {'username': ['exact', 'icontains']}
    )

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(id=user.id)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, obj)
        return super().retrieve(request, pk=pk)


class GroupViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows groups to be viewed or edited."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAllowedUser)
    filter_fields = fields('id', 'name')


class LocationViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows locations to be viewed or edited."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'address'
    )


class ContactViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows contacts to be viewed or edited."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'name', {'email': ['exact', 'icontains']},
        'phone',
    )


class AmenityViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows amenities to be viewed or edited."""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class ServiceViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows services to be viewed or edited."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class PotentialViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows potentials to be viewed or edited."""
    queryset = Potential.objects.all()
    serializer_class = PotentialSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class PropertyViewSetMixin(QueryArgumentsMixin, EagerLoadingMixin):
    """Mixin that allows properties to be viewed or edited."""
    queryset = Property.objects.all().order_by('-post_date')

    select_related = {
        'location': 'location', 
        'contact': 'contact', 
        'owner': 'owner'
    }
    prefetch_related = {
        'pictures': 'pictures', 
        'amenities': 'amenities', 
        'services': 'services', 
        'potentials': 'potentials', 
        'other_features': 'other_features'
    }

    serializer_class = PropertySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_fields = fields(
        {'id': ['exact', 'in']},  'available_for', {'price': ['exact', 'lt', 'gt']},
        'is_price_negotiable', 'currency', 'location', 'owner',
        {'contact': ['exact', 'in']}, 'type',
        {'post_date': ['exact', 'lt', 'gt', 'range']},
    )
    search_fields = [
        'location__address',
        'descriptions'
    ]

    def destroy(self, request, pk=None):
        """Function for deleting property and its associated components"""
        property = get_object_or_404(self.queryset, pk=pk)
        location = property.location
        contact = property.contact
        pictures = property.pictures

        # Don't use bulk deletion because it doesn't use overriden delete
        # on Picture Model, so with it picture files won't be deleted
        for picture in pictures.get_queryset():
            picture.delete()

        property.delete()
        location.delete()
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def contains_lookup(self, request, queryset, field):
        ids = json.loads(request.query_params.get(field, "[]"))
        field = field.replace("__contains", "__in")

        if(not ids):
            return queryset

        lookup = {field: ids}
        queryset = queryset.filter(**lookup).distinct()
        return queryset

    def filter_with_contains_lookup(self, queryset):
        request = self.request
        qs = self.contains_lookup(request, queryset, "services__contains")
        qs = self.contains_lookup(request, qs, "amenities__contains")
        qs = self.contains_lookup(request, qs, "potentials__contains")
        return qs

    def get_nearby_properties(self, queryset):
        """
        Return nearby properties
        """
        DEFAULT_RADIUS_TO_SCAN = 1000 # In meters
        
        longitude = self.request.query_params.get('longitude', None)
        latitude = self.request.query_params.get('latitude', None)

        if longitude is None and latitude is None:
            # No filtering by latitude & longitude
            return queryset
            
        radius_to_scan = self.request.query_params.get(
            'radius_to_scan',
            DEFAULT_RADIUS_TO_SCAN
        )

        data = {
            'longitude': longitude,
            'latitude': latitude,
            'radius_to_scan': radius_to_scan
        }
        serializer = NearbyLocationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        SRID = 4326
        location_to_scan_from = Point(
            serializer.data.get('longitude'),
            serializer.data.get('latitude'),
            srid=SRID
        )

        qs = queryset.annotate(
            distance=Distance('location__point', location_to_scan_from)
        )
        
        qs = qs.filter(
            distance__lt=serializer.data.get('radius_to_scan')
        )

        qs = qs.order_by('distance')

        return qs

    def get_queryset(self):
        """Do a custom search of location in every field of Location model"""
        queryset = super().get_queryset()
        qs = self.filter_with_contains_lookup(queryset)
        qs = self.get_nearby_properties(qs)
        return qs


class PropertyViewSet(PropertyViewSetMixin, viewsets.ModelViewSet):
    """API endpoint that allows Property to be viewed or edited."""


class PropertyPictureViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Property Picture to be viewed or edited."""
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = (IsAuthenticated, BelongsToPropertyOwnedByAuthenticatedUser)
    filter_fields = fields('id', 'property', 'tooltip')


class SingleRoomViewSet(PropertyViewSet):
    """API endpoint that allows SingleRoom to be viewed or edited."""
    queryset = SingleRoom.objects.all().order_by('-post_date')
    serializer_class = SingleRoomSerializer
    filter_fields = fields(
        'price_rate_unit', 'rooms__type', 'rooms__count'
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class HouseViewSet(PropertyViewSet):
    """API endpoint that allows House to be viewed or edited."""
    queryset = House.objects.all().order_by('-post_date')
    serializer_class = HouseSerializer
    filter_fields = fields(
        'price_rate_unit',
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class ApartmentViewSet(PropertyViewSet):
    """API endpoint that allows Apartment to be viewed or edited."""
    queryset = Apartment.objects.all().order_by('-post_date')
    serializer_class = ApartmentSerializer
    filter_fields = fields(
        'price_rate_unit',
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class LandViewSet(PropertyViewSet):
    """API endpoint that allows Land to be viewed or edited."""
    queryset = Land.objects.all().order_by('-post_date')
    serializer_class = LandSerializer
    filter_fields = fields(
        {'square_meters': ['gt', 'lt', 'exact']}
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class FrameViewSet(PropertyViewSet):
    """API endpoint that allows Frame to be viewed or edited."""
    queryset = Frame.objects.all().order_by('-post_date')
    serializer_class = FrameSerializer
    filter_fields = fields(
        'price_rate_unit',
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class OfficeViewSet(PropertyViewSet):
    """API endpoint that allows Office to be viewed or edited."""
    queryset = Office.objects.all().order_by('-post_date')
    serializer_class = OfficeSerializer
    filter_fields = fields(
        'price_rate_unit',
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class HostelViewSet(PropertyViewSet):
    """API endpoint that allows Hostel to be viewed or edited."""
    queryset = Hostel.objects.all().order_by('-post_date')
    serializer_class = HostelSerializer
    filter_fields = fields(
        'price_rate_unit',
    )
    filter_fields = {**PropertyViewSet.filter_fields, **filter_fields}


class FeatureViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows PropertyFeature to be viewed or edited."""
    queryset = Feature.objects.all().order_by('-id')
    serializer_class = FeatureSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', 'property', 'name', 'value')


class PropertyAvailabilityViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        Return options for available_for field for each property type
        """
        return Response(PROPERTIES_AVAILABILITY)

    def retrieve(self, request, pk=None):
        """
        Return options for available_for field for a given property type
        """
        property_type = pk
        try:
            availability = PROPERTIES_AVAILABILITY[property_type]
        except KeyError:
            msg = f'Property type `{property_type}` is not defined.'
            return Response({'detail': msg}, status=404)
        return Response(availability)


class RoomTypeViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows PropertyFeature to be viewed or edited."""
    queryset = RoomType.objects.all().order_by('-id')
    serializer_class = RoomTypeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_fields = fields('id', 'code', 'name')
    pagination_class = None


class FavouritePropertiesViewSet(PropertyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint that returns user's favourite properties"""
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return user's favourite properties
        """
        user = self.request.user
        queryset = super().get_queryset()
        fav_ids = user.fav_properties.values_list('id')
        qs = queryset.filter(id__in=fav_ids)
        return qs
        

class NearbyPropertiesViewSet(PropertyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint that returns nearby properties from a specified point"""
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return nearby properties
        """
        DEFAULT_RADIUS_TO_SCAN = 1000 # In meters
        
        longitude = self.request.query_params.get('longitude', None)
        latitude = self.request.query_params.get('latitude', None)
        radius_to_scan = self.request.query_params.get(
            'radius_to_scan',
            DEFAULT_RADIUS_TO_SCAN
        )

        data = {
            'longitude': longitude,
            'latitude': latitude,
            'radius_to_scan': radius_to_scan
        }
        serializer = NearbyLocationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        SRID = 4326
        location_to_scan_from = Point(
            serializer.data.get('longitude'),
            serializer.data.get('latitude'),
            srid=SRID
        )

        queryset = super().get_queryset()

        qs = queryset.annotate(
            distance=Distance('location__point', location_to_scan_from)
        )
        
        qs = qs.filter(
            distance__lt=serializer.data.get('radius_to_scan')
        )

        qs = qs.order_by('distance')

        return qs
