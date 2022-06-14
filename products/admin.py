from django.contrib import admin
from .models import HomePage, Product
from django.template.defaultfilters import truncatechars
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def Description(self, product):
        return truncatechars(product.desc, 50)
    list_display = ['name', 'Description',
                    'category', 'price', 'inventory', 'discount']
    list_editable = ['inventory', 'discount']
    list_filter = ['category']


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ['tagline']
