from django.urls import path
from .views import (index,ashram_detail,add_meeting,
                    add_attendee,add_activity,create_activity,
                    add_to_gallery,create_ashram,
                    admin_approval)

urlpatterns = [
    path('', index, name="ashram"),
    path('detail/<str:slug>/',ashram_detail,name="AshramDetail"),
    path('add/meeting/',add_meeting,name="AddMeeting"),
    path('add/attendee/',add_attendee,name="AddAttendee"),
    path('add/activity/category/',add_activity,name="AddActivityCategory"),
    path('create/activity/',create_activity,name="CreateActivity"),
    path('add/gallery/',add_to_gallery,name="AddToGallery"),
    path('create/ashram/',create_ashram,name="CreateAshram"),
    path('admin_approval/',admin_approval,name="ImageAdminApprovalAshram")
]
