from django.db import models

from bandhuapp.models import Profile

class Publication(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    thumb = models.ImageField(upload_to='publications')
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