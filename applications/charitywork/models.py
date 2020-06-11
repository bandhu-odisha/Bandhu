from django.db import models

# Create your models here.

class Charity(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    # photos = models.Foriegnkey()