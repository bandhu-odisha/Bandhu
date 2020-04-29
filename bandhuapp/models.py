from django.db import models
from accounts.models import User
# Create your models here.

class Profile(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=350)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=350)
    profession = models.CharField(max_length=500)
    dob = models.DateTimeField()

    def __str__(self):
        return self.full_name

# class Charity(models.Model):
#     charityName = models.CharField(max_length=350)
#     charityDescription = models.TextField(max_length=1000)
#     charityType = models.choices()
#     charityAddressLine1 = models.CharField(max_length=350)
#     charityCity = models.CharField(max_length=100)

#     def __str__(self):
#         return self.charityName