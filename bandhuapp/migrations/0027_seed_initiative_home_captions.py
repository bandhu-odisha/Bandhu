# Generated manually

from django.db import migrations

from bandhuapp.initiative_home_captions import INITIATIVE_CAPTIONS


def seed_initiative_home_captions(apps, schema_editor):
    for app_label, captions in INITIATIVE_CAPTIONS.items():
        HomePage = apps.get_model(app_label, 'HomePage')
        for page in HomePage.objects.all():
            changed = False
            if captions.get('en') and not (getattr(page, 'image_caption_en', None) or '').strip():
                page.image_caption_en = captions['en']
                changed = True
            if captions.get('or') and not (getattr(page, 'image_caption_or', None) or '').strip():
                page.image_caption_or = captions['or']
                changed = True
            if changed:
                page.save(update_fields=['image_caption_en', 'image_caption_or'])


class Migration(migrations.Migration):

    dependencies = [
        ('bandhuapp', '0026_initiatives_per_app_homepage'),
        ('ankurayan', '0016_homepage_hero_captions'),
        ('anandakendra', '0003_homepage_hero_captions'),
        ('ashram', '0003_homepage_hero_captions'),
        ('charitywork', '0003_homepage_hero_captions'),
        ('publications', '0004_homepage_hero_captions'),
        ('patriotism', '0007_homepage_hero_captions'),
        ('sevavrata', '0007_homepage_hero_captions'),
        ('prasantaraktadan', '0007_homepage_hero_captions'),
    ]

    operations = [
        migrations.RunPython(seed_initiative_home_captions, migrations.RunPython.noop),
    ]
