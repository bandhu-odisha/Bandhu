from django.contrib import admin
from .models import HomePage, Product
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ['tagline']
