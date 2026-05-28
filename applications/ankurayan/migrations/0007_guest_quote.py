from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0006_add_dummy_guests'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='quote',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Quote / What they said'),
        ),
    ]
