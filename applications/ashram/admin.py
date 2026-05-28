from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

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

    def response_add(self, request, obj, post_url_continue=None):
        next_site = request.GET.get('next')
        if next_site == 'bandhughar_details':
            return HttpResponseRedirect(reverse('ashram:AshramDetail', args=(obj.slug,)))

        return super(AshramAdmin, self).response_add(request, obj, post_url_continue)

admin.site.register(ActivityCategory)
admin.site.register(Activity)
admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Attendee)
admin.site.register(Photo)
admin.site.register(HomePage)
