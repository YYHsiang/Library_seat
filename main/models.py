from django.db import models
from django.db.models.base import Model
from ip_camera.models import Camera

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Camera_Data(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    occupy = models.BooleanField()

class Seat(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    camera = models.ManyToManyField(Camera) #every seat is capture by multiple cameras
    camera_data = models.ManyToManyField(Camera_Data) # data from each camera

    seat_number = models.IntegerField()
    seat_position_x = models.FloatField(max_length=200)
    seat_position_y = models.FloatField(max_length=200)
    occupy = models.BooleanField()

class Occupy_History(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
