from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prasantaraktadan', '0004_program_activity_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='ashram',
            name='is_published',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, this entry is visible to all visitors on the program page.',
            ),
        ),
    ]
