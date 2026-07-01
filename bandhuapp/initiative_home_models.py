"""Shared fields for per-initiative HomePage models."""

from django.db import models

HERO_IMAGE_HELP = 'Large image beside the text. Leave empty to use the first gallery photo.'


class InitiativeHeroCaptionMixin(models.Model):
    """Bilingual quote below the hero image on entry/detail pages."""

    image_caption_en = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Image caption (English)',
        help_text='Short quote below the hero image.',
    )
    image_caption_or = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Image caption (Odia)',
    )

    class Meta:
        abstract = True


# Backwards-compatible alias for HomePage models.
InitiativeHomePageMixin = InitiativeHeroCaptionMixin
