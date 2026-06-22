from django.db import models

from bandhuapp.models import Profile

# Create your models here.

class Ashram(models.Model):
    name = models.CharField(max_length=50)
    locality = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    reports = models.TextField(
        max_length=5000,
        blank=True,
        help_text='Optional rich text for reports (links, notes).',
    )
    address = models.CharField(max_length=250)
    image = models.ImageField(upload_to='prasantaraktadan/thumbnails/')
    slug = models.SlugField()
    is_published = models.BooleanField(
        default=False,
        help_text='When enabled, this entry is visible to all visitors on the program page.',
    )
    # admin = models.ForeignKey(Profile,blank=True,null=True,on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Prasanta Raktadan Shibir'
        verbose_name_plural = 'Prasanta Raktadan Shibir'
        unique_together = (('name', 'locality'),)

    def __str__(self):
        return f'{self.name} - {self.locality}'

class ActivityCategory(models.Model):
    """Program-wide category shared across all years in this initiative."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return self.name

class Activity(models.Model):
    ashram = models.ForeignKey(Ashram, on_delete=models.CASCADE, related_name='activities')
    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT, related_name='activities')
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.ashram.name} - {self.name} ({self.category.name})'

class Event(models.Model):
    ashram = models.ForeignKey(Ashram, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    thumb = models.ImageField(upload_to='prasantaraktadan/events')
    date = models.DateField()

    def __str__(self):
        return f'{self.ashram.name} - {self.name}'

class Meeting(models.Model):
    ashram = models.ForeignKey(Ashram, on_delete=models.CASCADE)
    schedule = models.DateTimeField()
    topic = models.CharField(max_length=250)
    location = models.CharField(max_length=100)
    agenda = models.TextField()
    minutes = models.FileField(upload_to='prasantaraktadan/meeting/%Y-%m-%d')

    def __str__(self):
        return f'{self.ashram.name} - {self.topic} ({self.schedule})'

class Attendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13)
    # or
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prasantaraktadan_attendees',
    )

    def __str__(self):
        return f'{self.meeting.ashram.name} - {self.meeting.schedule} - {self.name}'

    def save(self, *args, **kwargs):
        if self.profile is not None:
            self.name = f'{self.profile.first_name} {self.profile.last_name}'
            self.email = self.profile.user.email
            self.contact_no = self.profile.contact_no
        super(Attendee, self).save(*args, **kwargs)

def picture_upload_path(instance, filname):
    return f'prasantaraktadan/{instance.ashram.name}/{filename}'

class Photo(models.Model):
    ashram = models.ForeignKey(Ashram, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='prasantaraktadan/')
    approved = models.BooleanField(default=False)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

class AshramReportLink(models.Model):
    ashram = models.ForeignKey(
        Ashram, on_delete=models.CASCADE, related_name='report_links', db_constraint=False,
    )
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500, help_text='Google Drive, PDF host, or any URL.')
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Report link'
        verbose_name_plural = 'Report links'
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title


class AshramReportFile(models.Model):
    ashram = models.ForeignKey(
        Ashram, on_delete=models.CASCADE, related_name='report_files', db_constraint=False,
    )
    file = models.FileField(upload_to='prasantaraktadan/reports/%Y')
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Report file'
        verbose_name_plural = 'Report files'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.file.name


class AshramInvitationLetter(models.Model):
    ashram = models.OneToOneField(
        Ashram,
        on_delete=models.CASCADE,
        related_name='invitation_letter',
        db_constraint=False,
    )
    file = models.FileField(
        upload_to='prasantaraktadan/invitation_letters/',
        help_text='PDF or image invitation letter.',
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Invitation letter'
        verbose_name_plural = 'Invitation letters'

    def __str__(self):
        return f'Invitation — {self.ashram.name}'


class HomeGalleryPhoto(models.Model):
    picture = models.ImageField(upload_to='prasantaraktadan/home_gallery/')
    approved = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return 'Prasanta Raktadan Shibir home gallery photo'


class HomePage(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name="Tagline (Bold)")
    description = models.TextField(max_length=3000)
    picture = models.ImageField(upload_to='prasantaraktadan/index')
    banner_image = models.ImageField(upload_to='prasantaraktadan/banner')

    class Meta:
        verbose_name = 'Prasanta Raktadan Shibir Home Page'
        verbose_name_plural = 'Prasanta Raktadan Shibir Home Page'

    def __str__(self):
        return 'Prasanta Raktadan Shibir Home Page Content'
