"""Shared Django admin for initiative program HomePage models."""

from django.contrib import admin

from bandhuapp.initiative_home_admin import INITIATIVE_HERO_HELP


class InitiativeProgramHomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Text',
            {
                'fields': ('description',),
                'description': (
                    'Main body text for the program page (HTML allowed). '
                    'Also summarized on the main homepage under “Support a Cause”.'
                ),
            },
        ),
        (
            'Hero image & caption',
            {
                'fields': ('picture', 'image_caption_en', 'image_caption_or'),
                'description': INITIATIVE_HERO_HELP,
            },
        ),
    )
