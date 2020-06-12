from django.urls import path
from . import views

urlpatterns = [
    path('<int:year>/', views.index, name="ankurayan"),
]
