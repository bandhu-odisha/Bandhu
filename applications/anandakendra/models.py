import datetime
from django.db import models

from bandhuapp.models import Profile

# Create your models here.

class AnandaKendra(models.Model):
    name = models.CharField(max_length=50)
    locality = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.name} - {self.locality}'

class ActivityCategory(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.kendra.name} - {self.name}'

class Activity(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.kendra.name} - {self.name} ({self.category.name})'

class Student(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    guardian_name = models.CharField(max_length=50)
    school_class = models.IntegerField()
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    village = models.CharField(max_length=50)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.kendra.name} - {self.name} ({self.school_class})'

class Acharya(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    dob = models.DateField(verbose_name="Date of Birth", default=datetime.datetime.now)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.kendra.name} - {self.name}'

def picture_upload_path(instance, filname):
    return f'anandakendra/{instance.kendra.name}/{filename}'

class Photo(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_upload_path)
    category = models.ForeignKey(ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.kendra.name} - {self.category.name} - {self.activity.name}'
