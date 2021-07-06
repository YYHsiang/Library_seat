from django.contrib import admin
from .models import Location,Seat,Occupy_History
# Register your models here.
admin.site.register(Location)
admin.site.register(Seat)
admin.site.register(Occupy_History)