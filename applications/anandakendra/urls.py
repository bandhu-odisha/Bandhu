from django.urls import path
from .views import (index,anandkendra_detail,add_acharya,
                    enroll_student,add_activity,create_activity,
                    add_to_gallery,create_anandakendra,admin_approval)

urlpatterns = [
    path('', index, name="anandakendra"),
    path('detail/<str:slug>/',anandkendra_detail,name="AnandkendraDetail"),
    path('add/acharya/',add_acharya,name="AddAcharya"),
    path('enroll/student/',enroll_student,name="EnrollStudent"),
    path('add/activity/category/',add_activity,name="AnandakendraAddActivityCategory"),
    path('create/activity/',create_activity,name="AnandakendraCreateActivity"),
    path('add/gallery/',add_to_gallery,name="AnandakendraAddToGallery"),
    path('create/anandakendra/',create_anandakendra,name="CreateAnandaKendra"),
    path('admin_approval/',admin_approval,name="AdminImageApproval")
]
