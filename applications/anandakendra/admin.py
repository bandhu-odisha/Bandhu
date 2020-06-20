from django.contrib import admin

from .models import (
    AnandaKendra, ActivityCategory, Activity,
    Student, Acharya, Photo,
)

# Register your models here.
admin.site.register(AnandaKendra)
admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Student)
admin.site.register(Acharya)
admin.site.register(Photo)
