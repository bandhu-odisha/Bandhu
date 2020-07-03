from django.contrib import admin
from .models import Profile, RecentActivity
# from .models import Profile, Charity, Activity, Meeting, Ashram
# Register your models here.

admin.site.register(Profile)
# admin.site.register(Charity)
# admin.site.register(Activity)
# admin.site.register(Meeting)
# admin.site.register(Ashram)
admin.site.register(RecentActivity)
