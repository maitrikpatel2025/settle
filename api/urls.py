from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as auth_view

from api import views

router = routers.DefaultRouter()
router.register(r'profile-pictures', views.ProfilePictureViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'potentials', views.PotentialViewSet)
router.register(r'features', views.FeatureViewSet)
router.register(r'amenities', views.AmenityViewSet)
router.register(r'property-pictures', views.PropertyPictureViewSet)

router.register(r'properties', views.PropertyViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'houses', views.HouseViewSet)
router.register(r'apartments', views.ApartmentViewSet)
router.register(r'lands', views.LandViewSet)
router.register(r'frames', views.FrameViewSet)
router.register(r'offices', views.OfficeViewSet)
router.register(r'hostels', views.HostelViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', views.AuthenticateUser.as_view()),
    path('register/', views.RegisterUser.as_view()),
    path('properties-availability/', views.PropertiesAvailability.as_view()),
    path('properties-availability/<str:type>/', views.PropertyAvailability.as_view()),
    path('my-fav-properties/', views.FavouriteProperties.as_view()),
]
