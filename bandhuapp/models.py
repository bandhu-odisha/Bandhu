from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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
        return f'{self.first_name} {self.last_name} - {self.user.email}'

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def get_complete_address(self):
        if self.street_address2:
            return f'{self.street_address1}, {self.street_address2}, {self.city} - {self.pincode}, {self.state}'
        return f'{self.street_address1}, {self.city} - {self.pincode}, {self.state}'


class RecentActivity(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True, verbose_name="Date/ Start Date (Optional)")
    end_date = models.DateField(null=True, blank=True, verbose_name="End Date (Optional)")
    link = models.CharField(max_length=500, verbose_name='Link (not required if inserting file)', null=True, blank=True)
    notice_file = models.FileField(upload_to='notice_files', verbose_name='Notice File (Optional)', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Recent Activities'

    def __str__(self):
        return f'{self.title} - {self.start_date}'

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Start date cannot come after end date!")
        super(RecentActivity, self).save(*args, **kwargs)

@receiver(post_save, sender=RecentActivity)
def create_link_for_file(sender, instance=None, created=False, **kwargs):
    """Update link to direct to File field."""
    if instance.notice_file:
        instance.link = instance.notice_file.url
    if instance.link is None:
        instance.link = '#'
    sender.objects.filter(id=instance.id).update(link=instance.link)

class Photo(models.Model):
    picture = models.ImageField(upload_to='bandhuapp/gallery')
    caption = models.TextField(max_length=500, null=True, blank=True)
    tags = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Gallery Photo'
        verbose_name_plural = 'Gallery Photos'

    def __str__(self):
        return f'Photo{self.id}'

class Initiatives(models.Model):
    ankurayan_desc = models.TextField(max_length=500, verbose_name='Anurayan Tagline')
    ankurayan_thumb = models.ImageField(upload_to='main_page/initiatives', verbose_name='Ankurayan Thumbnail')
    kendra_desc = models.TextField(max_length=500, verbose_name='Anandakendra Tagline')
    kendra_thumb = models.ImageField(upload_to='main_page/initiatives', verbose_name='Anandakendra Thumbnail')
    bandhughar_desc = models.TextField(max_length=500, verbose_name='Bandhughar Tagline')
    bandhughar_thumb = models.ImageField(upload_to='main_page/initiatives', verbose_name='Bandhughar Thumbnail')
    otheract_desc = models.TextField(max_length=500, verbose_name='Other Activities Tagline')
    otheract_thumb = models.ImageField(upload_to='main_page/initiatives', verbose_name='Other Activities Thumbnail')
    publications_desc = models.TextField(max_length=500, verbose_name='Our Publications Tagline')
    publications_thumb = models.ImageField(upload_to='main_page/initiatives', verbose_name='Our Publications Thumbnail')

    class Meta:
        verbose_name_plural = 'Initiatives Section'

    def __str__(self):
        return 'Initiative Section Details'

class AboutUs(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name='About Us Tagline (Bold)')
    desc = models.TextField(max_length=3000, verbose_name='About Us Description')

    class Meta:
        verbose_name_plural = 'About Us Section'

    def __str__(self):
        return 'About Us Section Details'

class Mission(models.Model):
    sanskar_tagline = models.TextField(max_length=500, verbose_name='Sanskar Tagline (Bold)')
    sanskar_desc = models.TextField(max_length=3000, verbose_name='Sanskar Description')
    swaraj_tagline = models.TextField(max_length=500, verbose_name='Swaraj Tagline (Bold)')
    swaraj_desc = models.TextField(max_length=3000, verbose_name='Swaraj Description')
    swabalamban_tagline = models.TextField(max_length=500, verbose_name='Swabalamban Tagline (Bold)')
    swabalamban_desc = models.TextField(max_length=3000, verbose_name='Swabalamban Description')

    class Meta:
        verbose_name_plural = 'Our Mission Section'

    def __str__(self):
        return 'Our Mission Section Details'

class SanskarCarousel(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='bandhuapp/sanskar')

    class Meta:
        verbose_name = 'Sanskar Photo'
        verbose_name_plural = 'Sanskar Photos'

    def __str__(self):
        return f'Photo{self.id}'

class SwarajCarousel(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='bandhuapp/swaraj')

    class Meta:
        verbose_name = 'Swaraj Photo'
        verbose_name_plural = 'Swaraj Photos'

    def __str__(self):
        return f'Photo{self.id}'

class SwabalambanCarousel(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='bandhuapp/swabalamban')

    class Meta:
        verbose_name = 'Swabalamban Photo'
        verbose_name_plural = 'Swabalamban Photos'

    def __str__(self):
        return f'Photo{self.id}'

class Volunteer(models.Model):
    title = models.CharField(max_length=50)
    tagline = models.TextField(max_length=1500)

    class Meta:
        verbose_name_plural = 'Volunteer Section'

    def __str__(self):
        return 'Volunteer Section Details'

class Gallery(models.Model):
    tagline = models.TextField(max_length=500)

    class Meta:
        verbose_name_plural = 'Gallery Section'

    def __str__(self):
        return 'Gallery Section Details'

class Contact(models.Model):
    address = models.CharField(max_length=200)
    contact_no = models.CharField(max_length=50, verbose_name='Contact Number')
    email = models.CharField(max_length=50)
    facebook_link = models.CharField(max_length=150)
    twitter_link = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'Contact Us Section'

    def __str__(self):
        return 'Contact Us Section Details'

class HomePage(models.Model):
    banner_image = models.ImageField(upload_to='bandhuapp/banner')

    class Meta:
        verbose_name = 'Bandhu Home Page'
        verbose_name_plural = 'Bandhu Home Page'

    def __str__(self):
        return 'Bandhu Home Page Content'
