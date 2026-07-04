from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from bandhuapp.initiative_program_admin import InitiativeProgramHomePageAdmin
from bandhuapp.initiative_entry_admin import entry_hero_fieldset

from .models import (
    Ashram, ActivityCategory, Activity,
    Event, Meeting, Attendee, Photo, HomePage
)

# Register your models here.

@admin.register(Ashram)
class AshramAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', 'locality')}
    list_display = ('name', 'locality')
    ordering = ('name',)
    search_fields = ('name', 'locality')
    fieldsets = (
        (None, {
            'fields': ('name', 'locality', 'slug', 'address', 'description', 'reports', 'is_published'),
        }),
        entry_hero_fieldset('image'),
    )

    def response_add(self, request, obj, post_url_continue=None):
        next_site = request.GET.get('next')
        if next_site == 'prasantaraktadan_details':
            return HttpResponseRedirect(reverse('prasantaraktadan:AshramDetail', args=(obj.slug,)))

        return super(AshramAdmin, self).response_add(request, obj, post_url_continue)

admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Attendee)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'ashram', 'approved', 'activity')
    list_filter = ('approved',)
    list_editable = ('approved',)


admin.site.register(HomePage, InitiativeProgramHomePageAdmin)
