from django.urls import path
from . import views

urlpatterns = [
    path('', views.charity_work, name="charity_work"),
]
