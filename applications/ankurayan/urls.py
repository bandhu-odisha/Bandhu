from django.urls import path
from .views import (index,ankurayan_detail,add_guest,
                    add_participant,add_activity,create_activity,
                    add_to_gallery,add_winners,create_ankurayan,
                    admin_approval)

urlpatterns = [
    path('', index, name="ankurayan"),
    path('detail/<str:slug>/',ankurayan_detail,name="AnkurayanDetail"),
    path('add/guest/',add_guest,name="AddGuest"),
    path('add/participant/',add_participant,name="AddParticipant"),
    path('add/activity/category/',add_activity,name="AddActivityCategory"),
    path('create/activity/',create_activity,name="CreateActivity"),
    path('add/gallery/',add_to_gallery,name="AddToGallery"),
    path('add/winners/',add_winners,name="AddWinners"),
    path('create/ankurayan/',create_ankurayan,name="CreateAnkurayan"),
    path('admin_approval/',admin_approval,name="ImageAdminApproval")
]
