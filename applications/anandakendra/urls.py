from django.urls import path
from .views import (index,anandkendra_detail,add_acharya,
                    enroll_student,add_activity,create_activity,
                    add_winners,add_to_gallery)

urlpatterns = [
    path('', index, name="anandakendra"),
    path('detail/<str:slug>/',anandkendra_detail,name="AnandkendraDetail"),
    path('add/acharya/',add_acharya,name="AddAcharya"),
    path('enroll/student/',enroll_student,name="EnrollStudent"),
    path('add/activity/category/',add_activity,name="AddActivityCategory"),
    path('create/activity/',create_activity,name="CreateActivity"),
    path('add/winners/',add_winners,name="AddWinners"),
    path('add/gallery/',add_to_gallery,name="AddToGallery")
]
