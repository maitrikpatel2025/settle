from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as auth_view

from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'location', views.LocationViewSet)
router.register(r'property-owner', views.PropertyOwnerViewSet)
router.register(r'phone', views.PhoneViewSet)
router.register(r'service', views.ServiceViewSet)
router.register(r'potential', views.PotentialViewSet)
router.register(r'property', views.PropertyViewSet)
router.register(r'picture', views.PictureViewSet)
router.register(r'room', views.RoomViewSet)
router.register(r'house', views.HouseViewSet)
router.register(r'apartment', views.ApartmentViewSet)
router.register(r'land', views.LandViewSet)
router.register(r'frame', views.FrameViewSet)
router.register(r'office', views.OfficeViewSet)
router.register(r'hostel', views.HostelViewSet)
router.register(r'hall', views.HallViewSet)
router.register(r'feature', views.FeatureViewSet)
router.register(r'property-feature', views.PropertyFeatureViewSet)
router.register(r'amenity', views.AmenityViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', auth_view.obtain_auth_token),
]
