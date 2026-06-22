from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .helpers import _createHash, core_team_card_lines, proper_case
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
    profile_pic = models.ImageField(upload_to='profile_photos', null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.user.email}'

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    PROFILE_PROPER_CASE_FIELDS = (
        'first_name', 'last_name', 'profession', 'city', 'state',
        'street_address1', 'street_address2',
    )

    def save(self, *args, **kwargs):
        for field in self.PROFILE_PROPER_CASE_FIELDS:
            value = getattr(self, field, None)
            if isinstance(value, str) and value.strip():
                setattr(self, field, proper_case(value))
        super().save(*args, **kwargs)

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
    # active
    # new
    # pin (maybe for future)

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

class HeroSlide(models.Model):
    image    = models.ImageField(upload_to='bandhuapp/hero')
    title    = models.CharField(max_length=120)
    subtitle = models.TextField(max_length=400, blank=True)
    order    = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'

    def __str__(self):
        return f'{self.order}: {self.title}'


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


class AnnualReport(models.Model):
    """Year-wise annual report — PDF upload or external link (e.g. Google Drive)."""

    year = models.PositiveIntegerField(
        unique=True,
        help_text='Financial / report year (e.g. 2024 for FY 2023–24).',
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text='Optional label shown in the footer. Defaults to “Annual Report {year}”.',
    )
    pdf_file = models.FileField(
        upload_to='bandhuapp/annual_reports/',
        blank=True,
        null=True,
        help_text='Upload a PDF. Leave empty if you only use an external link.',
    )
    external_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='Google Drive or other public link to the PDF.',
    )
    is_published = models.BooleanField(
        default=True,
        help_text='Show this report in the site footer.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'Annual report'
        verbose_name_plural = 'Annual reports'

    def __str__(self):
        label = (self.title or '').strip() or f'Annual Report {self.year}'
        return f'{label} ({self.year})'

    def clean(self):
        super().clean()
        has_pdf = bool(self.pdf_file)
        has_url = bool((self.external_url or '').strip())
        if not has_pdf and not has_url:
            raise ValidationError(
                'Provide either a PDF file or an external link (e.g. Google Drive).'
            )

    def display_title(self):
        return (self.title or '').strip() or f'Annual Report {self.year}'

    def get_public_url(self, request=None):
        """Prefer uploaded PDF; otherwise use external URL."""
        if self.pdf_file:
            try:
                url = self.pdf_file.url
            except ValueError:
                url = None
            if url:
                if request and url.startswith('/'):
                    return request.build_absolute_uri(url)
                return url
        external = (self.external_url or '').strip()
        return external or None


class HomePage(models.Model):
    banner_image = models.ImageField(upload_to='bandhuapp/banner')
    visitors_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Bandhu Home Page'
        verbose_name_plural = 'Bandhu Home Page'

    def __str__(self):
        return 'Bandhu Home Page Content'


class HomeVisitor(models.Model):
    """Testimonial shown in the homepage Our Visitors carousel."""

    AVATAR_CHOICES = (
        ('man', 'Man (default illustration)'),
        ('woman', 'Woman (default illustration)'),
    )

    name = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100, help_text='Shown as profession in the profile popup.')
    place = models.CharField(max_length=100, help_text='City or region, e.g. Bhubaneswar.')
    avatar = models.CharField(max_length=10, choices=AVATAR_CHOICES, default='man')
    about = models.TextField(max_length=1000, blank=True, default='')
    quote = models.TextField(max_length=500)
    facebook_url = models.URLField(max_length=255, blank=True, default='')
    linkedin_url = models.URLField(max_length=255, blank=True, default='')
    photo = models.ImageField(
        upload_to='bandhuapp/visitors',
        blank=True,
        null=True,
        help_text='Optional. Leave empty to use the default man/woman illustration.',
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        db_index=True,
        help_text='Lower numbers appear first in the carousel.',
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Homepage visitor'
        verbose_name_plural = 'Homepage visitors'

    def __str__(self):
        return self.name

class UrlData(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=255,validators=[URLValidator()])
    hash = models.CharField(
        max_length=255, primary_key=True, default=_createHash)
    times_followed = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f'{self.url} to {self.hash}'


class CurrentUpdates(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    desc = models.CharField(max_length=255)
    url = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        ordering = ["-created_at"]


class Designation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    rank = models.IntegerField(default=9999)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank} - {self.title}"

    def save(self, *args, **kwargs):
        if isinstance(self.title, str) and self.title.strip():
            self.title = proper_case(self.title)
        super().save(*args, **kwargs)


class DesignationRole(models.Model):
    """Specific position within a designation (e.g. President under Office Bearers)."""
    created_at = models.DateTimeField(auto_now_add=True)
    designation = models.ForeignKey(
        Designation, on_delete=models.CASCADE, related_name="roles"
    )
    title = models.CharField(max_length=255)
    rank = models.IntegerField(default=9999)

    class Meta:
        ordering = ["rank", "title"]
        unique_together = [["designation", "title"]]
        verbose_name = "designation role"
        verbose_name_plural = "designation roles"

    def __str__(self):
        return f"{self.designation.title}: {self.title}"

    def save(self, *args, **kwargs):
        if isinstance(self.title, str) and self.title.strip():
            self.title = proper_case(self.title)
        super().save(*args, **kwargs)


class Staff(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="staff", unique=True
    )
    webpage = models.URLField(blank=True)
    about = models.TextField(max_length=1000)
    qualifications = models.TextField(
        max_length=2000,
        blank=True,
        default="",
        help_text="Education and qualifications (one per line). Shown on the staff profile only.",
    )

    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profile.get_full_name

class PeoplesDesignation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="designations"
    )
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    role = models.ForeignKey(
        DesignationRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
        help_text="Office bearer position (only for designations that define roles).",
    )
    desc = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Optional occupation or short note shown under the role.",
    )
    rank = models.IntegerField(default=9999)

    class Meta:
        unique_together = [["staff", "designation", "role"]]
        ordering = ["designation__rank", "rank"]
        verbose_name = "people designation"
        verbose_name_plural = "people designations"

    def clean(self):
        if self.role_id and self.role.designation_id != self.designation_id:
            raise ValidationError(
                {"role": "Role must belong to the selected designation."}
            )
        if not self.designation_id:
            return
        title = self.designation.title
        if title == "Core Team":
            if self.role_id:
                raise ValidationError(
                    {"role": "Core Team does not use a position; leave Role empty."}
                )
            duplicate = PeoplesDesignation.objects.filter(
                staff_id=self.staff_id, designation_id=self.designation_id
            )
            if self.pk:
                duplicate = duplicate.exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError("This person is already on Core Team.")
        elif title in ("Office Bearers", "Other"):
            if not self.role_id:
                raise ValidationError(
                    {"role": "Office Bearers requires a position (President, Secretary, etc.)."}
                )

    def __str__(self):
        role = f" ({self.role.title})" if self.role_id else ""
        return f"{self.staff.profile.get_full_name} — {self.designation.title}{role}"

    def save(self, *args, **kwargs):
        if isinstance(self.desc, str) and self.desc.strip():
            self.desc = proper_case(self.desc.strip())
        super().save(*args, **kwargs)

    @property
    def display_lines(self):
        """People cards: office bearer [role, profession]; core team [profession] only."""
        if self.role_id:
            occupation = (self.desc or "").strip()
            if not occupation and self.staff_id:
                occupation = (self.staff.profile.profession or "").strip()
            lines = [proper_case(self.role.title)]
            if occupation:
                lines.append(proper_case(occupation))
            return lines
        if self.designation_id and self.designation.title == "Core Team":
            return core_team_card_lines(
                self.staff.profile.profession if self.staff_id else "",
                self.desc,
                self.staff.about if self.staff_id else "",
            )
        occupation = (self.desc or "").strip()
        if not occupation and self.staff_id:
            occupation = (self.staff.profile.profession or "").strip()
        if occupation:
            return [proper_case(occupation)]
        return [""]


class StaffExperience(models.Model):
    """User-submitted experience/review for a staff profile."""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="experiences")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class StaffExperiencePhoto(models.Model):
    """Photo attached to a staff experience submission."""
    experience = models.ForeignKey(
        StaffExperience, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="experience_photos/%Y/%m/")
    caption = models.CharField(max_length=255, blank=True, help_text="Optional tag or caption for this photo")

    class Meta:
        verbose_name_plural = "Staff experience photos"


class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True)
    script = models.TextField(max_length=1000)
    duration = models.CharField(
        max_length=20,
        blank=True,
        help_text='Optional display length, e.g. 5:42 or 1:05:30 (from YouTube).',
    )
    class Meta:
        ordering = ["-created_at"]