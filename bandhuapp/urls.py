from django.urls import path,include
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index_react, name="home"),  # Modern React landing
    path('classic/', views.index, name="home_classic"),
    path('api/landing/', views.landing_api, name="landing_api"),
    # path('complete_profile/', views.complete_profile, name="complete_profile"),
    path('profile/', views.profile_page, name="profile_page"),
    # path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('photos/add_image/', views.add_image, name='add_image'),
    path('photos/approve_image/', views.approve_image, name='approve_image'),
    path('user_profile_data/', views.extract_user_data, name="extract_user_data"),
    path('links/<str:hash>', views.external_link,name="external_url_redirect"),
    path("people/", views.people, name="people_page"),
    path("people/<str:id>/", views.staff_profile, name="staff_profile"),
    path("people/<str:id>/experiences/", views.staff_experiences, name="staff_experiences"),
    path("people/<str:id>/share-experience/", views.staff_share_experience, name="staff_share_experience"),
    path(
        "people/<str:id>/experience/<int:experience_id>/edit/",
        views.staff_edit_experience,
        name="staff_edit_experience",
    ),
    path(
        "people/<str:id>/experience/<int:experience_id>/delete/",
        views.staff_delete_experience,
        name="staff_delete_experience",
    ),
    path("sanskar/", views.pillar_sanskar, name="pillar_sanskar"),
    path("swaraj/", views.pillar_swaraj, name="pillar_swaraj"),
]
