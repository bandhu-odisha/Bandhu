from django.db import models
from django.template.defaultfilters import slugify

from bandhuapp.models import Profile

# Create your models here.

class Ankurayan(models.Model):
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    theme = models.TextField(max_length=250)
    description = models.TextField(max_length=1000)
    logo = models.ImageField(upload_to='ankurayan/logo')
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'Ankurayan'

    def __str__(self):
        return f'Ankurayan {self.year}'

    def save(self,*args,**kwargs):
        str1 = self.year
        self.slug = slugify(str1)
        super(Ankurayan,self).save(*args,**kwargs)

class Participant(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    school_class = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name}'

class Guest(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    profession = models.CharField(max_length=100)
    about = models.TextField(max_length=500, null=True, blank=True)
    email = models.EmailField()
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name} ({self.profession})'


class ActivityCategory(models.Model):
    CATEGORY = (
        ('Cultural','Cultural'),
        ('Sports','Sports'),
        ('Debate','Debate'),
    )

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100,choices=CATEGORY)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.name}'

class Activity(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    activity_date = models.DateField()
    winner = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="Winner")
    runner_up1 = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="FirstRunnerUp")
    runner_up2 = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="SecondRunnerUp")


    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name} ({self.category.name})'

class Photo(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='ankurayan/%Y')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.ankurayan.year}'
