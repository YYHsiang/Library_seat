from django.urls import path
from . import views

urlpatterns = [
    path("ipcamera/", views.livefe, name="ipcamera"),
    path("cameras/", views.camera_list, name="camera_list"),
]
