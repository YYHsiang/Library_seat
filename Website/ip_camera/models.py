from django.db import models

# Create your models here.

class Camera(models.Model):
    name = models.CharField(max_length=100, unique= True)
    password = models.CharField(max_length=100, null=True)
    ip_address = models.CharField(max_length=300)

    frame = models.ImageField(upload_to='img', blank=True)
    thumbnail = models.ImageField(upload_to='img/thumbnail', blank=True)