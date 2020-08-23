from django.contrib import admin

from .models import (
    Ashram, ActivityCategory, Activity,
    Event, Meeting, Attendee, Photo, HomePage
)

# Register your models here.
admin.site.register(Ashram)
admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Attendee)
admin.site.register(Photo)
admin.site.register(HomePage)
