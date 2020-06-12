from django.db import models

from bandhuapp.models import Profile

# Create your models here.

class Ankurayan(models.Model):
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    theme = models.TextField(max_length=250)
    description = models.TextField(max_length=1000)
    logo = models.ImageField(upload_to='ankurayan/logo')

    class Meta:
        verbose_name_plural = 'Ankurayan'

    def __str__(self):
        return f'Ankurayan {self.year}'

class Participant(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER, default='M')
    school = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
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
    # or
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name} ({self.profession})'

    def save(self, *args, **kwargs):
        if self.profile is not None:
            self.name = f'{self.profile.first_name} {self.profile.first_name}'
            self.profession = self.profile.profession
            self.email = self.profile.user.email
            self.contact_no = self.profile.contact_no
        super(Guest, self).save(*args, **kwargs)


class ActivityCategory(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name}'

class Activity(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name} ({self.category.name})'

class Winner(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ankurayan.year} - {self.activity.name} ({self.rank})'

class Photo(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='ankurayan')
    category = models.ForeignKey(ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.ankurayan.year} - {self.category.name} - {self.activity.name}'
