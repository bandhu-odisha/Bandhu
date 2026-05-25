# Generated manually for multiple office bearer roles per staff member.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bandhuapp", "0016_homevisitor"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="peoplesdesignation",
            unique_together={("staff", "designation", "role")},
        ),
    ]
