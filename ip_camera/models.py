from django.db import models

# Create your models here.

class Camera(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, null=True)
    ip_address = models.CharField(max_length=300)

    frame = models.ImageField(upload_to='img')
    thumbnail = models.ImageField(upload_to='img')