from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_published')
    list_editable = ('sort_order', 'is_published')
    ordering = ('sort_order', 'name')
    fieldsets = (
        (None, {
            'fields': (
                'name', 'label', 'image', 'sort_order', 'is_published',
            ),
            'description': 'Each word in the product label is title-cased automatically when you save (e.g. premium rice → Premium Rice).',
        }),
        ('Modal description', {
            'fields': ('intro_lead', 'intro_text', 'nutritional_highlights', 'quality_promise'),
            'description': (
                'Opening phrase is shown in bold automatically (plain text, no HTML). '
                'Quality promise: one item per line — each line appears as its own row on the product modal.'
            ),
        }),
    )
