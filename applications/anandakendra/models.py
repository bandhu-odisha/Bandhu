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
    image = models.ImageField(upload_to='anandkendra/kendras',null=True,blank=True)
    slug = models.SlugField(blank=True,null=True)
    admin = models.ManyToManyField(Profile,blank=True)

    def __str__(self):
        return f'{self.name} - {self.locality}'

    def save(self,*args,**kwargs):
        str1 = self.name
        str2 = self.locality
        self.slug = slugify(str1+'-'+str2)
        super(AnandaKendra,self).save(*args,**kwargs)

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
    school_class = models.CharField(max_length=6)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.kendra.name} - {self.name} ({self.school_class})'

class ActivityCategory(models.Model):
    CATEGORY = (
        ('Cultural','Cultural'),
        ('Sports','Sports'),
        ('Debate','Debate'),
    )

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.category} - {self.name}'

class Activity(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    activity_date = models.DateField(default=timezone.now)
    winner = models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True,related_name="Winner")
    runner_up1 = models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True,related_name="FirstRunnerUp")
    runner_up2 = models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True,related_name="SecondRunnerUp")

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.kendra.name} - {self.name} ({self.category.name})'

class Acharya(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    acharya_id = models.ForeignKey(Profile,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.kendra.name} - {self.acharya_id.first_name} {self.acharya_id.last_name}'

def picture_upload_path(instance, filname):
    return f'anandakendra/{instance.kendra.name}/{filename}'

class Photo(models.Model):
    kendra = models.ForeignKey(AnandaKendra, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='anandkendra/activities')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.kendra.name} - {self.picture}'
