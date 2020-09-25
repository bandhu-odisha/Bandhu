from django.urls import path,include
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    # path('complete_profile/', views.complete_profile, name="complete_profile"),
    path('profile/', views.profile_page, name="profile_page"),
    # path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('photos/add_image/', views.add_image, name='add_image'),
    path('photos/approve_image/', views.approve_image, name='approve_image'),
    path('user_profile_data/', views.extract_user_data, name="extract_user_data"),
    path('notice-archive/', views.notice_archive, name="notice_archive"),
    path('get_active_notice/', views.get_active_notice, name="active_notice"),
]
