from django.urls import path,include
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('cause3/', views.cause3, name="cause3"),
    path('cause4/', views.cause4, name="cause4"),
    path('cause5/', views.cause5, name="cause5"),
    # path('complete_profile/', views.complete_profile, name="complete_profile"),
    path('profile/', views.profile_page, name="profile_page"),
    # path('edit_profile/', views.edit_profile, name="edit_profile"),
]
