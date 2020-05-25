from django.db import models
from accounts.models import User
# Create your models here.

class Profile(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    dob = models.DateField(verbose_name="Date of Birth")
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    street_address1	= models.CharField(verbose_name="Address Line 1", max_length=255)
    street_address2	= models.CharField(verbose_name="Address Line 2", max_length=255, blank=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=25)
    pincode	= models.CharField(max_length=10)
    profession = models.CharField(max_length=500)
    profile_pic = models.ImageField(upload_to='profile_photos', default='profile_photos/man.png')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

# class Charity(models.Model):
#     charityName = models.CharField(max_length=350)
#     charityDescription = models.TextField(max_length=1000)
#     charityType = models.choices()
#     charityAddressLine1 = models.CharField(max_length=350)
#     charityCity = models.CharField(max_length=100)

#     def __str__(self):
#         return self.charityName