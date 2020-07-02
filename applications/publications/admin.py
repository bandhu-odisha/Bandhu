from django.contrib import admin

from .models import Publication, PublicationMedia
from .forms import PublicationForm

@admin.register(Publication)
class PublicationModelAdmin(admin.ModelAdmin):
    form = PublicationForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title_stripped', 'thumb', 'created')
    list_filter = ('created',)

# In case image should be removed from album.
@admin.register(PublicationMedia)
class PublicationMediaModelAdmin(admin.ModelAdmin):
    list_display = ('alt', 'publication')
    list_filter = ('publication', 'created')