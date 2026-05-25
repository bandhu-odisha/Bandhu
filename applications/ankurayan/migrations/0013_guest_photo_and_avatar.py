from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0012_reset_example_guests'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='avatar',
            field=models.CharField(
                choices=[('man', 'Man (default illustration)'), ('woman', 'Woman (default illustration)')],
                default='man',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='guest',
            name='photo',
            field=models.ImageField(
                blank=True,
                help_text='Optional. Leave empty to use the default man/woman illustration.',
                null=True,
                upload_to='ankurayan/guests',
            ),
        ),
    ]
