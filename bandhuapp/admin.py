from django.contrib import admin
from .models import (
    Profile, RecentActivity, Photo, Initiatives, AboutUs,
    Mission, Volunteer, Gallery, Contact,
)

# Register your models here.

admin.site.register(Profile)
admin.site.register(Initiatives)
admin.site.register(AboutUs)
admin.site.register(Mission)
admin.site.register(Volunteer)
admin.site.register(Gallery)
admin.site.register(Contact)

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'notice_file')

    def save_model(self, request, obj, form, change):
        """Updating link and deleting file if file is removed."""
        if change and not obj.notice_file:
            pre_instance = RecentActivity.objects.filter(id=obj.id)
            if (pre_instance.exists() and pre_instance[0].notice_file and
                    obj.link == pre_instance[0].notice_file.url):
                pre_instance[0].notice_file.delete(False)
                obj.link = '#'
        super().save_model(request, obj, form, change)

@admin.register(Photo)
class PublicationModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'picture')
