from django.urls import path
from . import views
from .views import ChartData
from django.views.generic import TemplateView #as_view() function

urlpatterns = [
    path("analysis/", views.analysis, name='analysis'),
    path("api/chart/data/", ChartData.as_view()),
]
