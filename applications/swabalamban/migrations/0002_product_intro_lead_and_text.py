import re

from django.db import migrations, models


def split_intro_html(apps, schema_editor):
    Product = apps.get_model('swabalamban', 'Product')
    pattern = re.compile(r'^<strong>(.*?)</strong>\s*(.*)$', re.IGNORECASE | re.DOTALL)
    for product in Product.objects.all():
        intro = (product.intro or '').strip()
        if not intro:
            continue
        match = pattern.match(intro)
        if match:
            product.intro_lead = match.group(1).strip()
            product.intro_text = match.group(2).strip()
        else:
            product.intro_lead = ''
            product.intro_text = intro
        product.save(update_fields=['intro_lead', 'intro_text'])


class Migration(migrations.Migration):

    dependencies = [
        ('swabalamban', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='intro_lead',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Shown in bold at the start of the modal description (plain text, no HTML).',
                max_length=200,
                verbose_name='Opening phrase',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='intro_text',
            field=models.TextField(
                default='',
                help_text='Rest of the opening paragraph (plain text).',
                max_length=2000,
                verbose_name='Description',
            ),
            preserve_default=False,
        ),
        migrations.RunPython(split_intro_html, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='product',
            name='intro',
        ),
    ]
