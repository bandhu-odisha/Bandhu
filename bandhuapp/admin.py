from django.contrib import admin
from .models import (
    Profile, RecentActivity, Photo, Initiatives, AboutUs,
    Mission, Volunteer, Gallery, Contact,
)

# Register your models here.

admin.site.register(Profile)
admin.site.register(RecentActivity)
admin.site.register(Initiatives)
admin.site.register(AboutUs)
admin.site.register(Mission)
admin.site.register(Volunteer)
admin.site.register(Gallery)
admin.site.register(Contact)

@admin.register(Photo)
class PublicationModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'picture')
