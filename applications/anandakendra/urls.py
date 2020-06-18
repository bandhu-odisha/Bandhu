from django.urls import path
from .views import (index,anandkendra_detail,add_acharya,
                    enroll_student,add_activity,create_activity,
                    add_to_gallery,create_anandakendra)

urlpatterns = [
    path('', index, name="anandakendra"),
    path('detail/<str:slug>/',anandkendra_detail,name="AnandkendraDetail"),
    path('add/acharya/',add_acharya,name="AddAcharya"),
    path('enroll/student/',enroll_student,name="EnrollStudent"),
    path('add/activity/category/',add_activity,name="AddActivityCategory"),
    path('create/activity/',create_activity,name="CreateActivity"),
    path('add/gallery/',add_to_gallery,name="AddToGallery"),
    path('create/anandakendra/',create_anandakendra,name="CreateAnandaKendra")
]
