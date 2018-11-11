from django.contrib import admin
from .models import Location, PropertyOwner, Phone, Service, Potential, Property, Picture, Room, House, Apartment, Hostel, Frame, Land, Hall, Office
# Register your models here.

admin.site.register(Apartment)
admin.site.register(Frame)
admin.site.register(Hall)
admin.site.register(Hostel)
admin.site.register(House)
admin.site.register(Land)
admin.site.register(Location) 
admin.site.register(Office)
admin.site.register(Phone)
admin.site.register(Picture) 
admin.site.register(Potential) 
admin.site.register(Property)
admin.site.register(PropertyOwner)
admin.site.register(Room)
admin.site.register(Service)
