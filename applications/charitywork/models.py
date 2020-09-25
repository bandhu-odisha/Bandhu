from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from bandhuapp.models import Profile

# Create your models here.

class Charity(models.Model):
    title = models.CharField(max_length=60)
    purpose = models.CharField(max_length=60)   # Cyclone/Earthquake
    description = models.TextField()
    location = models.CharField(max_length=60)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='charity_work/charities/')
    slug = models.SlugField()
    # admin = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,blank=True)

    class Meta:
        unique_together = (('title', 'purpose', 'location'), )
        verbose_name = 'Other Activity'
        verbose_name_plural = 'Other Activities'

    def __str__(self):
        return f'{self.title} - {self.location}'


class Volunteer(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    # or
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.charity.title}'

    def save(self, *args, **kwargs):
        if self.profile is not None:
            self.name = f'{self.profile.first_name} {self.profile.last_name}'
            self.email = self.profile.user.email
            self.contact_no = self.profile.contact_no
        super(Volunteer, self).save(*args, **kwargs)

class Photo(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='charity_work/%Y')
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.charity.title}'

class Activity(models.Model):   # Donation/Food Supply
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    volunteers = models.ManyToManyField(Volunteer)
    date = models.DateField()
    thumb = models.ImageField(upload_to='charity_work/thumbnails', default='charity_work/thumbnails/activity.jpg')
    photo = models.ManyToManyField(Photo, related_name="charity_activity", blank=True)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.name} - {self.charity.title} '



class HomePage(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name="Tagline (Bold)")
    description = models.TextField(max_length=3000)
    picture = models.ImageField(upload_to='charity_work/index')
    banner_image = models.ImageField(upload_to='charity_work/banner')

    class Meta:
        verbose_name = 'Other Activities Home Page'
        verbose_name_plural = 'Other Activities Home Page'

    def __str__(self):
        return 'Other Activities Home Page Content'

