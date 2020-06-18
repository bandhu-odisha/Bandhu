from django.contrib import admin

from .models import (
    Ankurayan, Participant, Guest,
    ActivityCategory, Activity, Photo,
)

# Register your models here.
admin.site.register(Ankurayan)
admin.site.register(Participant)
admin.site.register(Guest)
admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Photo)