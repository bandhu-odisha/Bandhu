from django.urls import path
from . import views

app_name = 'ankurayan'
urlpatterns = [
    path('', views.index, name="ankurayan"),
    path('detail/<str:slug>/', views.ankurayan_detail,name="AnkurayanDetail"),
    path('add/guest/', views.add_guest,name="AddGuest"),
    path('add/participant/', views.add_participant,name="AddParticipant"),
    path('add/activity/category/', views.add_activity_category, name="AddActivityCategory"),
    path('create/activity/', views.create_activity,name="CreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AddToGallery"),
    path('add/winners/', views.add_winners,name="AddWinners"),
    path('new/', views.create_ankurayan,name="CreateAnkurayan"),
    path('admin_approval/', views.admin_approval,name="ImageAdminApproval")
]
