from django.urls import path

from . import views

app_name = 'publications'
urlpatterns = [
    path('', views.index, name='index'),
    path('<slug>/', views.publication_detail, name='publication'),
]