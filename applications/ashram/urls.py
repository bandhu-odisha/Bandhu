from django.urls import path
from . import views

app_name = 'ashram'
urlpatterns = [
    path('', views.index, name="ashram"),
    path('detail/<str:slug>/', views.ashram_detail,name="AshramDetail"),
    path('add/meeting/', views.add_meeting,name="AddMeeting"),
    path('add/attendee/', views.add_attendee,name="AddAttendee"),
    path('add/activity/category/', views.add_activity_category,name="AddActivityCategory"),
    path('create/activity/', views.create_activity,name="CreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AddToGallery"),
    path('create/ashram/', views.create_ashram,name="CreateAshram"),
    path('admin_approval/', views.admin_approval,name="ImageAdminApprovalAshram"),
    path('create/event/',views.create_event,name="CreateEventAshram")
]
