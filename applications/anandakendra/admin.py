from django.contrib import admin

from .models import (
    AnandaKendra, ActivityCategory, Activity,
    Event, Student, Acharya, Photo,
)

@admin.register(AnandaKendra)
class AnandaKendraAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name','locality')}
    list_display = ('name','locality', 'admin')
    ordering = ('name',)
    search_fields = ('name', 'admin__first_name','locality')

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','get_kendra',)
    list_filter = ('kendra__name',)
    ordering = ('kendra__name', 'name',)
    search_fields = ('name', 'kendra__name')

    def get_kendra(self, obj):
        return obj.kendra.name
    get_kendra.short_description = 'Anandakendra'
    get_kendra.admin_order_field = 'kendra__name'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name','category', 'get_kendra', 'activity_time')
    ordering = ('category__kendra__name', 'category__name', 'name')
    search_fields = ('name', 'category__kendra__name','category__name')

    def get_kendra(self, obj):
        return obj.category.kendra.name
    get_kendra.short_description = 'Anandakendra'
    get_kendra.admin_order_field = 'category__kendra__name'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name','get_kendra', 'date')
    ordering = ('kendra__name', '-date')
    search_fields = ('name', 'kendra__name', 'date')

    def get_kendra(self, obj):
        return obj.kendra.name
    get_kendra.short_description = 'Anandakendra'
    get_kendra.admin_order_field = 'kendra__name'

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
