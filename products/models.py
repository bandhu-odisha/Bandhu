from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField()
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    inventory = models.IntegerField()
    discount = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.ImageField(upload_to='products/products')

    def __str__(self):
        return self.name


class HomePage(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name="Tagline (Bold)")
    description = models.TextField(max_length=3000)
    picture = models.ImageField(upload_to='products/index')
    banner_image = models.ImageField(upload_to='products/banner')

    class Meta:
        verbose_name = 'Products Home Page'
        verbose_name_plural = 'Products Home Page'

    def __str__(self):
        return 'Products Home Page Content'
