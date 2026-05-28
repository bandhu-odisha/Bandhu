from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swabalamban', '0003_remove_product_card_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.RemoveField(
            model_name='product',
            name='slug',
        ),
    ]
