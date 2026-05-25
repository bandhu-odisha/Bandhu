from django.db import migrations, models


def copy_qualification_rows_to_staff_text(apps, schema_editor):
    Staff = apps.get_model("bandhuapp", "Staff")
    StaffQualification = apps.get_model("bandhuapp", "StaffQualification")
    for staff in Staff.objects.all():
        rows = StaffQualification.objects.filter(staff_id=staff.pk).order_by("since", "pk")
        if not rows.exists():
            continue
        lines = []
        for row in rows:
            line = f"{row.degree}, {row.institute} ({row.since.year}"
            if row.until:
                line += f" – {row.until.year}"
            else:
                line += " – present"
            line += ")"
            lines.append(line)
        if lines and not (staff.qualifications or "").strip():
            staff.qualifications = "\n".join(lines)
            staff.save(update_fields=["qualifications"])


class Migration(migrations.Migration):

    dependencies = [
        ("bandhuapp", "0017_multiple_office_bearer_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="staff",
            name="qualifications",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Education and qualifications (one per line). Shown on the staff profile only.",
                max_length=2000,
            ),
        ),
        migrations.RunPython(
            copy_qualification_rows_to_staff_text,
            migrations.RunPython.noop,
        ),
        migrations.DeleteModel(
            name="StaffQualification",
        ),
    ]
