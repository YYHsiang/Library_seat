from django import forms
from django.forms import fields
from .models import Camera

class Add_new_camera(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['name', 'ip_address']
