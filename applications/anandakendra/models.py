import datetime
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from bandhuapp.models import Profile

# Create your models here.

class AnandaKendra(models.Model):
    name = models.CharField(max_length=50)
    locality = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    address = models.CharField(max_length=250)
    image = models.ImageField(upload_to='anandakendra/kendras')
    slug = models.SlugField()
    # admin = models.ForeignKey(Profile,blank=True,null=True,on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Anandakendra'
        verbose_name_plural = 'Anandakendras'
        unique_together = (('name', 'locality'),)

    def __str__(self):
        return self.name

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
    school_class = models.CharField(max_length=15)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    address = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class ActivityCategory(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.kendra.name} - {self.name}'

class Photo(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='anandakendra/activities')
    approved = models.BooleanField(default=False)

class Activity(models.Model):
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    activity_time = models.CharField(max_length=100)
    photo = models.ManyToManyField(Photo, related_name="kendra_activity", blank=True)
    
    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.category.kendra.name} - {self.name} ({self.category.name})'

class Event(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    thumb = models.ImageField(upload_to='anandakendra/events')
    date = models.DateField()
    photo = models.ManyToManyField(Photo, related_name="kendra_event", blank=True)

    def __str__(self):
        return f'{self.kendra.name} - {self.name}'

class Acharya(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    acharya_id = models.ForeignKey(Profile,on_delete=models.CASCADE)

    def __str__(self):
        return self.acharya_id.first_name

def picture_upload_path(instance, filname):
    return f'anandakendra/{instance.kendra.name}/{filename}'

class HomePage(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name="Tagline (Bold)")
    description = models.TextField(max_length=3000)
    picture = models.ImageField(upload_to='anandakendra/index')
    banner_image = models.ImageField(upload_to='anandakendra/banner')

    class Meta:
        verbose_name = 'Anandakendra Home Page'
        verbose_name_plural = 'Anandakendra Home Page'

    def __str__(self):
        return 'Anandakendra Home Page Content'

