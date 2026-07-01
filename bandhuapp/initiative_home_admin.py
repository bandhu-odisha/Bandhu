from django.contrib import admin

INITIATIVE_TEXT_HELP = (
    'Description is shown on this initiative’s page and summarized on the main homepage '
    'under “Support a Cause”. HTML is allowed.'
)
INITIATIVE_HERO_HELP = 'Hero image appears beside the text. Gallery photos are added below.'


class InitiativeHomePageAdmin(admin.ModelAdmin):
    """Singleton home page editor for main initiative programs."""

    fieldsets = (
        ('Text', {
            'fields': ('description',),
            'description': INITIATIVE_TEXT_HELP,
        }),
        ('Hero image & caption', {
            'fields': ('picture', 'image_caption_en', 'image_caption_or'),
            'description': INITIATIVE_HERO_HELP,
        }),
    )

    def has_add_permission(self, request):
        return not self.model.objects.exists()
