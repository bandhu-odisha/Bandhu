from django.urls import path
from . import views

app_name = 'sevavrata'
urlpatterns = [
    path('', views.index, name="sevavrata"),
    path('detail/<str:slug>/', views.ashram_detail, name="AshramDetail"),
    path('detail/<str:slug>/upload-report/', views.upload_report_file, name="UploadReportFile"),
    path('detail/<str:slug>/add-report-link/', views.add_report_link, name="AddReportLink"),
    path('report-file/<int:pk>/delete/', views.delete_report_file, name="DeleteReportFile"),
    path('report-link/<int:pk>/delete/', views.delete_report_link, name="DeleteReportLink"),
    path('detail/<str:slug>/upload-invitation/', views.upload_invitation, name="UploadInvitation"),
    path('detail/<str:slug>/delete-invitation/', views.delete_invitation, name="DeleteInvitation"),
    path('detail/<str:slug>/update-description/', views.update_description, name="UpdateDescription"),
    path('add/meeting/', views.add_meeting,name="AddMeeting"),
    path('add/attendee/', views.add_attendee,name="AddAttendee"),
    path('add/activity/category/', views.add_activity_category,name="AddActivityCategory"),
    path('create/activity/', views.create_activity,name="CreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AddToGallery"),
    path('new/', views.create_ashram,name="CreateAshram"),
    path('admin_approval/', views.admin_approval,name="ImageAdminApprovalSevavrata"),
    path('create/event/',views.create_event,name="CreateEventSevavrata")
]
