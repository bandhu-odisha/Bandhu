from django.urls import path
from . import views

urlpatterns = [
    path('', views.ankurayan, name="ankurayan"),
]
