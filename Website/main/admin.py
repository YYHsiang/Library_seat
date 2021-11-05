from django.contrib import admin
from .models import Camera_Data, Location,Seat,OccupyHistory
# Register your models here.
admin.site.register(Location)
admin.site.register(Seat)
admin.site.register(OccupyHistory)
admin.site.register(Camera_Data)