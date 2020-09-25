from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from .models import (
    Ankurayan, Participant, Guest,
    ActivityCategory, Activity, Photo,
    HomePage,
)

@admin.register(Ankurayan)
class AnkurayanAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('year',)}
    list_display = ('theme','year','start_date','end_date')
    ordering = ('year',)
    search_fields = ('year','theme','locality')

    def response_add(self, request, obj, post_url_continue=None):
        next_site = request.GET.get('next')
        if next_site == 'ankurayan_details':
            return HttpResponseRedirect(reverse('ankurayan:AnkurayanDetail', args=(obj.slug,)))

        return super(AnkurayanAdmin, self).response_add(request, obj, post_url_continue)

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_year',)
    list_filter = ('ankurayan__year',)
    ordering = ('-ankurayan__year', 'name',)
    search_fields = ('name', 'ankurayan__year')

    def get_year(self, obj):
        return obj.ankurayan.year
    get_year.short_description = 'Ankurayan Year'
    get_year.admin_order_field = 'ankurayan__year'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'date', 'winner','runner_up1','runner_up1')
    ordering = ('-date',)
    search_fields = ('name', 'category__ankurayan__year','category__ankurayan__theme','category__name')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name','ankurayan', 'contact_no','school_class')
    ordering = ('name',)
    list_filter = ('school_class',)
    search_fields = ('name', 'ankurayan__year','ankurayan__theme',)

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name','ankurayan','profession','email','contact_no')
    ordering = ('name',)
    search_fields = ('name','ankurayan__year','ankurayan__theme',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('ankurayan','approved')
    ordering = ('ankurayan',)
    list_filter = ('approved',)
    search_fields = ('ankurayan__year','ankurayan__theme',)


admin.site.register(HomePage)
