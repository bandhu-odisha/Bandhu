from django.db import models

from bandhuapp.initiative_home_models import InitiativeHomePageMixin, HERO_IMAGE_HELP

from bandhuapp.models import Profile

class Publication(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    thumb = models.ImageField(upload_to='publications/thumb')
    by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_visible = models.BooleanField(default=True)
    created = models.DateTimeField()
    modified = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to="publications")
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title_stripped

    @property
    def title_stripped(self):
       from django.utils.html import strip_tags
       return strip_tags(self.title)

class HomePage(InitiativeHomePageMixin, models.Model):
    tagline = models.TextField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Tagline (bold)',
        help_text='Shown on the homepage initiative card and this page.',
    )
    description = models.TextField(max_length=3000, blank=True, default='')
    picture = models.ImageField(
        upload_to='publications/index',
        blank=True,
        verbose_name='Hero image',
        help_text=HERO_IMAGE_HELP,
    )

    class Meta:
        verbose_name = 'Publications Home Page'
        verbose_name_plural = 'Publications Home Page'

    def __str__(self):
        return 'Publications Home Page Content'
