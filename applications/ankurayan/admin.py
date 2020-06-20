from django.contrib import admin

from .models import (
    Ankurayan, Participant, Guest,
    ActivityCategory, Activity, Photo,
)

@admin.register(Ankurayan)
class AnkurayanAdmin(admin.ModelAdmin):
    list_display = ('theme','year','start_date','end_date', 'admin')
    ordering = ('year',)
    search_fields = ('year','theme','admin__first_name','locality')

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','category',)
    list_filter = ('category',)
    ordering = ('name',)
    search_fields = ('name', 'category')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name','ankurayan','category', 'activity_date','winner','runner_up1','runner_up1')
    ordering = ('-activity_date',)
    search_fields = ('name', 'ankurayan__year','ankurayan__theme','category__name')

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
    list_display = ('ankurayan','activity','approved')
    ordering = ('ankurayan',)
    list_filter = ('approved',)
    search_fields = ('activity', 'ankurayan__year','ankurayan__theme',)
