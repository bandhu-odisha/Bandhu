from django.contrib import admin

from .models import (
    Ashram, ActivityCategory, Activity,
    Meeting, Attendee, Photo,
)

# Register your models here.
admin.site.register(Ashram)
admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Meeting)
admin.site.register(Attendee)
admin.site.register(Photo)
