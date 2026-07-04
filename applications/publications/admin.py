from django.contrib import admin

from bandhuapp.initiative_home_admin import InitiativeHomePageAdmin

from .models import Publication, HomePage


@admin.register(Publication)
class PublicationModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title_stripped', 'thumb', 'created')
    list_filter = ('created',)


admin.site.register(HomePage, InitiativeHomePageAdmin)
