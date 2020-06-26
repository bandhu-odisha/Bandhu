from django.urls import path
from . import views

app_name = 'charitywork'
urlpatterns = [
    path('', views.index, name="charity_work"),
    path('detail/<str:slug>/', views.charity_detail,name="CharityDetail"),
    path('add/volunteers/', views.add_volunteers,name="AddVolunteers"),
    path('create/activity/', views.create_activity,name="CreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AddToGallery"),
    path('create/charity/', views.create_charity,name="CreateCharity"),
    path('admin_approval/', views.admin_approval,name="ImageAdminApprovalAshram")
]
