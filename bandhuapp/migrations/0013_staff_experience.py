import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bandhuapp", "0012_video_duration"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffExperience",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="experiences",
                        to="bandhuapp.staff",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="StaffExperiencePhoto",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="experience_photos/%Y/%m/")),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        help_text="Optional tag or caption for this photo",
                        max_length=255,
                    ),
                ),
                (
                    "experience",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="bandhuapp.staffexperience",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Staff experience photos",
            },
        ),
    ]
