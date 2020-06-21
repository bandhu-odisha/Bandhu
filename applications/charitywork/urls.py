from django.urls import path
from .views import (index,charity_detail,
                    add_volunteers,create_activity,
                    add_to_gallery,create_charity,
                    admin_approval)

urlpatterns = [
    path('', index, name="charity_work"),
    path('detail/<str:slug>/',charity_detail,name="CharityDetail"),
    path('add/volunteers/',add_volunteers,name="AddVolunteers"),
    path('create/activity/',create_activity,name="CreateActivity"),
    path('add/gallery/',add_to_gallery,name="AddToGallery"),
    path('create/charity/',create_charity,name="CreateCharity"),
    path('admin_approval/',admin_approval,name="ImageAdminApprovalAshram")
]
