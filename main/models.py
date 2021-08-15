from django.db import models

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Seat(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    camera_number = models.IntegerField()
    seat_number = models.IntegerField()
    seat_position_x = models.FloatField(max_length=200)
    seat_position_y = models.FloatField(max_length=200)
    occupy = models.BooleanField()


class Occupy_History(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
