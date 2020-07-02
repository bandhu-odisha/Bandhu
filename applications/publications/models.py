import uuid
from django.db import models
# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFit
# from ckeditor_uploader.fields import RichTextUploadingField
# from ckeditor.fields import RichTextField

from bandhuapp.models import Profile

class Publication(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    # thumb = ProcessedImageField(upload_to='Publications', processors=[ResizeToFit(300)], format='JPEG', options={'quality': 90})
    thumb = models.ImageField(upload_to='publications')
    by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_visible = models.BooleanField(default=True)
    created = models.DateTimeField()
    modified = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True)

    #def get_absolute_url(self):
    #    return reverse('album', kwargs={'slug':self.slug})

    def __str__(self):
        return self.title_stripped

    @property
    def title_stripped(self):
       from django.utils.html import strip_tags
       return strip_tags(self.title)

class PublicationMedia(models.Model):
    media = models.FileField(upload_to="publications")
    publication = models.ForeignKey('publication', on_delete=models.PROTECT)
    alt = models.CharField(max_length=255, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, default=uuid.uuid4, editable=False)