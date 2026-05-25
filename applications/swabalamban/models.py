import re

from django.db import models


class HomePage(models.Model):
    tagline = models.TextField(max_length=1000, verbose_name='Tagline (Bold)')
    description = models.TextField(max_length=3000)
    picture = models.ImageField(upload_to='swabalamban/index', blank=True)
    banner_image = models.ImageField(upload_to='swabalamban/banner', blank=True)
    caption_en = models.CharField(max_length=500, blank=True, default='')
    caption_or = models.CharField(max_length=500, blank=True, default='')
    order_note = models.TextField(
        max_length=1000,
        blank=True,
        default='',
        help_text='Text above the animated caption (e.g. WhatsApp ordering note).',
    )
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='Displayed in the order note, e.g. +91 98765 43210',
    )
    products_heading = models.CharField(
        max_length=300,
        blank=True,
        default='Quality produce from our Swabalamban initiative.',
    )

    class Meta:
        verbose_name = 'Swabalamban Home Page'
        verbose_name_plural = 'Swabalamban Home Page'

    def __str__(self):
        return 'Swabalamban Home Page Content'


class CarouselImage(models.Model):
    picture = models.ImageField(upload_to='swabalamban/carousel')
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Carousel image'
        verbose_name_plural = 'Carousel images'

    def __str__(self):
        return f'Carousel image {self.id}'


class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    label = models.CharField(max_length=120, help_text='Short label on the product card')
    image = models.ImageField(upload_to='swabalamban/products')
    intro_lead = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Opening phrase',
        help_text='Shown in bold at the start of the modal description (plain text, no HTML).',
    )
    intro_text = models.TextField(
        max_length=2000,
        verbose_name='Description',
        help_text='Rest of the opening paragraph (plain text).',
    )
    nutritional_highlights = models.TextField(
        max_length=2000,
        help_text='One bullet per line',
    )
    quality_promise = models.TextField(
        max_length=1000,
        help_text='One promise per line (shown separated by ·). Bullets (•) on one line also work.',
    )
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    @staticmethod
    def capitalize_label(value):
        """Title-case each word in the product card label (e.g. premium rice → Premium Rice)."""
        text = (value or '').strip()
        if not text:
            return text
        return text.lower().title()

    def save(self, *args, **kwargs):
        self.label = self.capitalize_label(self.label)
        super().save(*args, **kwargs)

    @property
    def modal_id(self):
        return f'productModal{self.pk}'

    @property
    def highlight_list(self):
        return [line.strip() for line in self.nutritional_highlights.splitlines() if line.strip()]

    @staticmethod
    def _clean_quality_promise_part(text):
        return re.sub(r'^[•·\-–—\s]+|[•·\-–—\s]+$', '', (text or '').strip())

    @property
    def quality_promise_list(self):
        """Split admin copy into phrases; rendered with · between each by default."""
        raw = (self.quality_promise or '').strip()
        if not raw:
            return []

        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if len(lines) > 1:
            return [self._clean_quality_promise_part(ln) for ln in lines if self._clean_quality_promise_part(ln)]

        parts = re.split(r'\s*[•·|;]\s*', raw)
        cleaned = [self._clean_quality_promise_part(p) for p in parts if self._clean_quality_promise_part(p)]
        if len(cleaned) > 1:
            return cleaned

        if ',' in raw:
            return [
                self._clean_quality_promise_part(p)
                for p in raw.split(',')
                if self._clean_quality_promise_part(p)
            ]

        single = self._clean_quality_promise_part(raw)
        return [single] if single else []
