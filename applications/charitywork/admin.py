from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from bandhuapp.initiative_home_admin import InitiativeHomePageAdmin
from bandhuapp.initiative_entry_admin import entry_hero_fieldset
from .models import (
    Charity, Volunteer, Activity, Photo, HomePage,
)
# Register your models here.

@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', 'purpose', 'location')}
    list_display = ('title', 'purpose', 'location', 'start_date')
    ordering = ('-start_date', 'title', 'location')
    search_fields = ('title', 'purpose', 'location')
    fieldsets = (
        (None, {
            'fields': ('title', 'purpose', 'location', 'slug', 'start_date', 'end_date', 'description'),
        }),
        entry_hero_fieldset('image'),
    )

    def response_add(self, request, obj, post_url_continue=None):
        next_site = request.GET.get('next')
        if next_site == 'activity_details':
            return HttpResponseRedirect(reverse('charitywork:CharityDetail', args=(obj.slug,)))

        return super(CharityAdmin, self).response_add(request, obj, post_url_continue)


admin.site.register(Volunteer)
admin.site.register(Activity)
admin.site.register(Photo)
admin.site.register(HomePage, InitiativeHomePageAdmin)
