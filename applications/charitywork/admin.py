from django.contrib import admin

from .models import Charity, Activity, Volunteer
# Register your models here.

admin.site.register(Charity)
admin.site.register(Volunteer)
admin.site.register(Activity)