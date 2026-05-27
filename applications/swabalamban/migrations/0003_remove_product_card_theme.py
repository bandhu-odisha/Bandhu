from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swabalamban', '0002_product_intro_lead_and_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='card_theme',
        ),
    ]
