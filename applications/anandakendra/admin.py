from django.contrib import admin

from .models import (
    AnandaKendra, ActivityCategory, Activity,
    Student, Acharya, Photo,
)

@admin.register(AnandaKendra)
class AnandaKendraAdmin(admin.ModelAdmin):
    list_display = ('name','locality', 'admin')
    ordering = ('name',)
    search_fields = ('name', 'admin__first_name','locality')

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','category',)
    list_filter = ('category',)
    ordering = ('name',)
    search_fields = ('name', 'category')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name','kendra','category', 'activity_date')
    ordering = ('-activity_date',)
    search_fields = ('name', 'kendra__name','category__name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','kendra','guardian_name', 'contact_no','school_class')
    ordering = ('name',)
    list_filter = ('school_class',)
    search_fields = ('name', 'kendra__name','guardian_name')

@admin.register(Acharya)
class AcharyaAdmin(admin.ModelAdmin):
    list_display = ('acharya_id','kendra',)
    ordering = ('acharya_id',)
    search_fields = ('acharya_id', 'kendra__name',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('kendra','activity','approved')
    ordering = ('kendra',)
    list_filter = ('approved',)
    search_fields = ('activity', 'kendra__name',)
