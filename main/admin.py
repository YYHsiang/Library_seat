from django.contrib import admin
from .models import Camera_Data, Location,Seat,Occupy_History
# Register your models here.
admin.site.register(Location)
admin.site.register(Seat)
admin.site.register(Occupy_History)
admin.site.register(Camera_Data)