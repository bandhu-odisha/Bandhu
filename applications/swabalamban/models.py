from django.db import models


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
        help_text='One promise per line (shown as a list on the product modal).',
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

    @property
    def quality_promise_list(self):
        return [line.strip() for line in (self.quality_promise or '').splitlines() if line.strip()]
