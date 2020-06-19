from django.db import models

from bandhuapp.models import Profile
# Create your models here.

class Charity(models.Model):
    #name
    date = models.DateTimeField()
    description = models.TextField(max_length=1000)
    #amount
    location = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Charity'
    
    def __str__(self):
        return f'Charity {self.date}'

class Volunteer(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name} {self.charity.date}'

class Photo(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='charity')

    def __str__(self):
        return f'{self.charity.date}'

class Activity(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.charity.date} {self.name}'