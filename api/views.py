import json

from django.db.models import Value
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django_restql.mixins import (
    EagerLoadingMixin, QueryArgumentsMixin
)
from django.contrib.auth.models import Group
from django.db.models.functions import Concat, Replace
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from api.permissions import (
    IsOwnerOrReadOnly, IsAllowedUser, HasGroupPermission, 
    BelongsToPropertyOwnedByAuthenticatedUser
)
from .models import (
    Location, Contact, Service, Potential, Property, PropertyPicture, Room,
    House, Apartment, Hostel, Frame, Land, Office, Feature, Amenity, User,
    ProfilePicture
)
from .serializers import (
    UserSerializer, GroupSerializer, LocationSerializer, FeatureSerializer,
    ContactSerializer, ServiceSerializer, PotentialSerializer,
    PropertySerializer, PropertyPictureSerializer, RoomSerializer, HouseSerializer,
    ApartmentSerializer, HostelSerializer, FrameSerializer, LandSerializer,
    OfficeSerializer, AmenitySerializer, ProfilePictureSerializer
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


class AuthenticateUser(ObtainAuthToken):
    """API endpoint that allows users to login and obtain auth token."""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
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


class RegisterUser(ObtainAuthToken):
    """API endpoint that allows users to register and obtain auth token."""
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        full_name = data.pop("full_name")
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
    """API endpoint that allows Location to be viewed or edited."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'country', 'region', 'distric', 'street1',
        'street2', 'longitude', 'latitude'
    )


class ContactViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Contact to be viewed or edited."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields(
        'id', 'name', {'email': ['exact', 'icontains']},
        'phone',
    )


class AmenityViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Amenity to be viewed or edited."""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class ServiceViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Service to be viewed or edited."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class PotentialViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Potential to be viewed or edited."""
    queryset = Potential.objects.all()
    serializer_class = PotentialSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = fields('id', {'name': ['icontains', 'startswith']})


class PropertyViewSet(QueryArgumentsMixin, EagerLoadingMixin, viewsets.ModelViewSet):
    """API endpoint that allows Property to be viewed or edited."""
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
        'id',  'available_for', {'price': ['exact', 'lt', 'gt']},
        'price_negotiation', 'currency', 'location', 'owner',
        {'contact': ['exact', 'in']},
        {'post_date': ['exact', 'lt', 'gt', 'range']},
    )
    search_fields = [
        'location__country',
        'location__region',
        'location__distric',
        'location__street1',
        'location__street2'
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
        if request.GET.get(field) is not None:
            ids = json.loads(request.GET[field])
            field = field.replace("__contains", "__in")
            for id in ids:
                lookup = {field: [id]}
                queryset = queryset.filter(**lookup)
        return queryset

    def filter_queryset(self, queryset):
        """Do a custom search of location in every field of Location model"""
        request = self.request
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        queryset = self.contains_lookup(request, queryset, "services__contains")
        queryset = self.contains_lookup(request, queryset, "amenities__contains")
        queryset = self.contains_lookup(request, queryset, "potentials__contains")
        return queryset


class PropertyPictureViewSet(QueryArgumentsMixin, viewsets.ModelViewSet):
    """API endpoint that allows Property Picture to be viewed or edited."""
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = (IsAuthenticated, BelongsToPropertyOwnedByAuthenticatedUser)
    filter_fields = fields('id', 'property', 'tooltip')


class RoomViewSet(PropertyViewSet):
    """API endpoint that allows Room to be viewed or edited."""
    queryset = Room.objects.all().order_by('-post_date')
    serializer_class = RoomSerializer
    filter_fields = fields(
        'price_rate_unit',
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
    filter_fields = fields()
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
