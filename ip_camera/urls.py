from django.urls import path
from . import views

urlpatterns = [
    path("livefe/<str:ip>", views.livefe, name="livefe"),
    path("cameras/", views.camera_list, name="camera_list"),
]
