from django.db import models
from django.template.defaultfilters import slugify

from bandhuapp.initiative_home_models import InitiativeHomePageMixin, HERO_IMAGE_HELP

from bandhuapp.models import Profile

# Create your models here.

class Ankurayan(InitiativeHomePageMixin, models.Model):
    year = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    theme = models.TextField(max_length=250)
    description = models.TextField(max_length=3000)
    reports = models.TextField(max_length=5000, blank=True, null=True, verbose_name='Reports')
    publications = models.TextField(max_length=5000, blank=True, null=True, verbose_name='Publications')
    visitors = models.TextField(max_length=5000, blank=True, null=True, verbose_name='Our Guests')
    start_date = models.DateField()
    end_date = models.DateField()
    logo = models.ImageField(
        upload_to='ankurayan/logo',
        verbose_name='Hero image',
        help_text=HERO_IMAGE_HELP,
    )
    slug = models.SlugField()
    # admin = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)

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
    school_class = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name}'

class Guest(models.Model):
    AVATAR_CHOICES = (
        ('man', 'Man (default illustration)'),
        ('woman', 'Woman (default illustration)'),
    )

    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=50)
    profession = models.CharField(max_length=100)
    avatar = models.CharField(max_length=10, choices=AVATAR_CHOICES, default='man')
    photo = models.ImageField(
        upload_to='ankurayan/guests',
        blank=True,
        null=True,
        help_text='Optional. Leave empty to use the default man/woman illustration.',
    )
    about = models.TextField(max_length=500, null=True, blank=True)
    quote = models.TextField(max_length=500, null=True, blank=True, verbose_name='Quote / What they said')
    email = models.EmailField(blank=True, default='')
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13, blank=True, default='')
    facebook_url = models.URLField(max_length=255, blank=True, default='', verbose_name='Facebook profile URL')
    linkedin_url = models.URLField(max_length=255, blank=True, default='', verbose_name='LinkedIn profile URL')
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        db_index=True,
        help_text='Lower numbers appear first in guest lists.',
    )

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name} ({self.profession})'


class GuestNote(models.Model):
    """Admin-only notes stored in DB per guest (separate from public profile fields)."""

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Guest note'
        verbose_name_plural = 'Guest notes'

    def __str__(self):
        return f'Note for {self.guest.name} ({self.created_at.date()})'


class ActivityCategory(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return f'{self.ankurayan.year} - {self.name}'

class Activity(models.Model):
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT, related_name='activities')
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    date = models.DateField()
    thumb = models.ImageField(upload_to='ankurayan/thumbnails', default='ankurayan/thumbnails/activity.jpg')
    winner = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="Winner")
    runner_up1 = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="FirstRunnerUp")
    runner_up2 = models.ForeignKey(Participant,on_delete=models.PROTECT,null=True,blank=True,related_name="SecondRunnerUp")


    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.category.ankurayan.year} - {self.name} ({self.category.name})'

class AnkurayanReportFile(models.Model):
    """Uploaded file for Reports tab (any file type)."""
    ankurayan = models.ForeignKey(
        Ankurayan, on_delete=models.CASCADE, related_name='report_files', db_constraint=False
    )
    file = models.FileField(upload_to='ankurayan/reports/%Y')
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Report file'
        verbose_name_plural = 'Report files'

    def __str__(self):
        return self.title or self.file.name


class AnkurayanInvitationLetter(models.Model):
    """One-page invitation letter per Ankurayan year (PDF or image)."""

    ankurayan = models.OneToOneField(
        Ankurayan,
        on_delete=models.CASCADE,
        related_name='invitation_letter',
        db_constraint=False,
    )
    file = models.FileField(
        upload_to='ankurayan/invitation_letters/',
        help_text='Single-page invitation letter (PDF or image).',
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Invitation letter'
        verbose_name_plural = 'Invitation letters'

    def __str__(self):
        return f'Invitation letter — Ankurayan {self.ankurayan.year}'


class AnkurayanPublicationFile(models.Model):
    """Uploaded file for Publications tab (any file type)."""
    ankurayan = models.ForeignKey(
        Ankurayan, on_delete=models.CASCADE, related_name='publication_files', db_constraint=False
    )
    file = models.FileField(upload_to='ankurayan/publications/%Y')
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Publication file'
        verbose_name_plural = 'Publication files'

    def __str__(self):
        return self.title or self.file.name


class Photo(models.Model):
    ankurayan = models.ForeignKey(Ankurayan, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='ankurayan/%Y')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.ankurayan.year}'

class HomePage(InitiativeHomePageMixin, models.Model):
    tagline = models.TextField(max_length=1000, verbose_name="Tagline (Bold)")
    description = models.TextField(max_length=3000)
    picture = models.ImageField(
        upload_to='ankurayan/index',
        blank=True,
        verbose_name='Hero image',
        help_text=HERO_IMAGE_HELP,
    )

    class Meta:
        verbose_name = 'Ankurayan Home Page'
        verbose_name_plural = 'Ankurayan Home Page'

    def __str__(self):
        return 'Ankurayan Home Page Content'
