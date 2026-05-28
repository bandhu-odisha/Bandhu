from django.urls import path
from . import views

app_name = 'ankurayan'
urlpatterns = [
    path('', views.index, name="ankurayan"),
    path('detail/<str:slug>/', views.ankurayan_detail, name="AnkurayanDetail"),
    path('detail/<str:slug>/update-section/', views.update_ankurayan_section, name="UpdateAnkurayanSection"),
    path('detail/<str:slug>/upload-report/', views.upload_ankurayan_report, name="UploadAnkurayanReport"),
    path('detail/<str:slug>/upload-publication/', views.upload_ankurayan_publication, name="UploadAnkurayanPublication"),
    path('report-file/<int:pk>/update/', views.update_ankurayan_report_file, name="UpdateAnkurayanReportFile"),
    path('report-file/<int:pk>/delete/', views.delete_ankurayan_report_file, name="DeleteAnkurayanReportFile"),
    path('publication-file/<int:pk>/update/', views.update_ankurayan_publication_file, name="UpdateAnkurayanPublicationFile"),
    path('publication-file/<int:pk>/delete/', views.delete_ankurayan_publication_file, name="DeleteAnkurayanPublicationFile"),
    path('add/guest/', views.add_guest,name="AddGuest"),
    path('guest/<int:pk>/update/', views.update_guest, name="UpdateGuest"),
    path('guest/<int:pk>/delete/', views.delete_guest, name="DeleteGuest"),
    path('add/participant/', views.add_participant,name="AddParticipant"),
    path('add/activity/category/', views.add_activity_category, name="AddActivityCategory"),
    path('create/activity/', views.create_activity,name="CreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AddToGallery"),
    path('add/winners/', views.add_winners,name="AddWinners"),
    path('new/', views.create_ankurayan,name="CreateAnkurayan"),
    path('admin_approval/', views.admin_approval,name="ImageAdminApproval")
]
