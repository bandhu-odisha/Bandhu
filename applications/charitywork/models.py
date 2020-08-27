from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from bandhuapp.models import Profile

# Create your models here.

class Charity(models.Model):
    title = models.CharField(max_length=500)
    purpose = models.CharField(max_length=500)   # Cyclone/Earthquake
    description = models.TextField()
    location = models.CharField(max_length=800)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='charity_work/charities/')
    slug = models.SlugField()
    admin = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,blank=True)

    def save(self,*args,**kwargs):
        str1 = self.title
        str2 = str(self.start_date)
        self.slug = slugify(str1 +'-'+ str2)
        super(Charity,self).save(*args,**kwargs)

    class Meta:
        unique_together = (('title', 'purpose', 'location'), )
        verbose_name = 'Other Activitie'
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


class Activity(models.Model):   # Donation/Food Supply
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    volunteers = models.ManyToManyField(Volunteer)
    date = models.DateField()
    thumb = models.ImageField(upload_to='charity_work/thumbnails', default='charity_work/thumbnails/activity.jpg')

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.name} - {self.charity.title} '


class Photo(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='ankurayan/%Y')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.charity.title}'
