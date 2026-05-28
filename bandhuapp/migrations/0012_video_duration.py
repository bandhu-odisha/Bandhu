from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandhuapp', '0011_auto_20240214_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='duration',
            field=models.CharField(
                blank=True,
                help_text='Optional display length, e.g. 5:42 or 1:05:30 (from YouTube).',
                max_length=20,
            ),
        ),
    ]
