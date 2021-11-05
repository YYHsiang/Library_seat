from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("location/<str:location_name>", views.location, name="location"),
    path("create/", views.create, name="create"),
]