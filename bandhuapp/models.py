from django.db import models
from accounts.models import User
from django.utils import timezone

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
        return f'{self.first_name} {self.last_name} - {self.user.email}'

# class Charity(models.Model):
# 	name = models.CharField(max_length=350)
# 	description = models.TextField(max_length=1000)
# 	# charity_type = models.choices(CHARITY_TYPES)
# 	# amount = models.IntegerField(min=0)
# 	date = models.DateTimeField()
# 	address = models.CharField(max_length=350)
# 	city = models.CharField(max_length=100)

# 	def __str__(self):
# 		return self.name

class Recent_Activity(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=350)
    date = models.DateTimeField()
    link = models.CharField(max_length=350)

    def __str__(self):
        return f'{self.name} {self.date}'
