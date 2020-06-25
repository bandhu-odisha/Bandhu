from django.urls import path
from . import views


app_name = 'anandakendra'
urlpatterns = [
    path('', views.index, name="anandakendra"),
    path('detail/<str:slug>/', views.anandkendra_detail,name="AnandkendraDetail"),
    path('add/acharya/', views.add_acharya,name="AddAcharya"),
    path('enroll/student/', views.enroll_student,name="EnrollStudent"),
    path('add/activity/category/', views.add_activity_category,name="AnandakendraAddActivityCategory"),
    path('create/activity/', views.create_activity,name="AnandakendraCreateActivity"),
    path('add/gallery/', views.add_to_gallery,name="AnandakendraAddToGallery"),
    path('create/anandakendra/', views.create_anandakendra,name="CreateAnandaKendra"),
    path('admin_approval/', views.admin_approval,name="AdminImageApproval")
]
