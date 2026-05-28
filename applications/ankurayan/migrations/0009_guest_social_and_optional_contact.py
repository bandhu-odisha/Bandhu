# Add social links and make email/contact optional for Guest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0008_populate_guest_quotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='facebook_url',
            field=models.URLField(blank=True, default='', max_length=255, verbose_name='Facebook profile URL'),
        ),
        migrations.AddField(
            model_name='guest',
            name='linkedin_url',
            field=models.URLField(blank=True, default='', max_length=255, verbose_name='LinkedIn profile URL'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='guest',
            name='contact_no',
            field=models.CharField(blank=True, default='', max_length=13, verbose_name='Contact Number'),
        ),
    ]
