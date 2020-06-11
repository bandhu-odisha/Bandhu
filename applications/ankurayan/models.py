from django.db import models

# Create your models here.

class Ankurayan(models.Model):
    theme = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="ankurayan/logos", default="ankurayan/logos/default.png")
    date = models.DateTimeField()

class Ankurayan_Activity(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # winner
