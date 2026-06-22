from django.db import migrations, models
import django.db.models.deletion

from bandhuapp.initiative_activity_migrate import migrate_activity_categories_to_program_scope


class Migration(migrations.Migration):

    dependencies = [
        ('patriotism', '0003_homegalleryphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='ashram',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='activities',
                to='patriotism.Ashram',
            ),
        ),
        migrations.RunPython(
            lambda apps, schema_editor: migrate_activity_categories_to_program_scope(
                apps, schema_editor, 'patriotism',
            ),
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='activity',
            name='ashram',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='activities',
                to='patriotism.Ashram',
            ),
        ),
        migrations.RemoveField(
            model_name='activitycategory',
            name='ashram',
        ),
        migrations.AlterField(
            model_name='activitycategory',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='activities',
                to='patriotism.ActivityCategory',
            ),
        ),
    ]
