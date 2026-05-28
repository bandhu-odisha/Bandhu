# Generated manually for Reports, Publications, Visitors tabs

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ankurayan',
            name='reports',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Reports'),
        ),
        migrations.AddField(
            model_name='ankurayan',
            name='publications',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Publications'),
        ),
        migrations.AddField(
            model_name='ankurayan',
            name='visitors',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Visitors'),
        ),
    ]
