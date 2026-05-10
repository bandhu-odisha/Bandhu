# Align visitors field verbose_name with model ('Our Guests')

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0009_guest_social_and_optional_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ankurayan',
            name='visitors',
            field=models.TextField(
                blank=True,
                max_length=5000,
                null=True,
                verbose_name='Our Guests',
            ),
        ),
    ]
