from django.contrib import admin
from django.utils.html import format_html, urlencode
from .models import (
    Designation, PeoplesDesignation, Profile, RecentActivity, Photo, Initiatives, AboutUs,
    Mission, SanskarCarousel, Staff, StaffContacts, StaffQualification, SwarajCarousel,
    SwabalambanCarousel, UrlData, Volunteer, Gallery, Contact,
    HomePage, CurrentUpdates
)

# Register your models here.

class SanskarCarouselInline(admin.StackedInline):
    model = SanskarCarousel

class SwarajCarouselInline(admin.StackedInline):
    model = SwarajCarousel

class SwabalambanCarouselInline(admin.StackedInline):
    model = SwabalambanCarousel

admin.site.register(Profile)
admin.site.register(Initiatives)
admin.site.register(AboutUs)

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    inlines = [SanskarCarouselInline, SwarajCarouselInline, SwabalambanCarouselInline]

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
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'picture', 'approved')

# @admin.register(SanskarCarousel)
# class SanskarCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

# @admin.register(SwarajCarousel)
# class SwarajCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

# @admin.register(SwabalambanCarousel)
# class SwabalambanCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

admin.site.register(HomePage)

@admin.register(UrlData)
class UrlDataAdmin(admin.ModelAdmin):
    list_display = ('url', 'shorten_url', 'times_followed', 'created')
    def shorten_url(self,url_data):
        return format_html('<a href="/links/{}">{}</a>', url_data.hash, url_data.hash)

@admin.register(CurrentUpdates)
class CurrentUpdatesAdmin(admin.ModelAdmin):
    list_display = ('created_at','desc','url')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('rank','title')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('profile','about')

@admin.register(PeoplesDesignation)
class PeoplesDesignationAdmin(admin.ModelAdmin):
    list_display = ('staff','designation')

@admin.register(StaffQualification)
class StaffQualificationAdmin(admin.ModelAdmin):
    list_display = ('staff','degree','institute')

@admin.register(StaffContacts)
class StaffContactsAdmin(admin.ModelAdmin):
    list_display = ('staff','facebook','twitter','linkedin')
