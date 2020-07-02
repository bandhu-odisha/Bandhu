from django.contrib import admin

from .models import Publication

@admin.register(Publication)
class PublicationModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title_stripped', 'thumb', 'created')
    list_filter = ('created',)