from django.urls import path
from . import views

urlpatterns = [
    path('', views.sanskarbarga, name="sanskarbarga"),
]
