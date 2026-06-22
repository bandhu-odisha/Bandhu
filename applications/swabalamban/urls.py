from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='pillar_swabalamban'),
    path('create/product/', views.create_product, name='CreateProduct'),
]
