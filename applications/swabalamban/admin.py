from django.contrib import admin

from .models import CarouselImage, HomePage, Product


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('tagline', 'description', 'picture', 'banner_image')}),
        ('Captions & ordering', {'fields': ('caption_en', 'caption_or', 'order_note', 'whatsapp_number')}),
        ('Products section', {'fields': ('products_heading',)}),
    )


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
                'Quality promise: one item per line — the site inserts · between items on the product modal.'
            ),
        }),
    )


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sort_order')
    list_editable = ('sort_order',)
    ordering = ('sort_order', 'id')
