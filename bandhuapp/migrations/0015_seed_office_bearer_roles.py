from django.db import migrations

OFFICE_BEARER_ROLE_TITLES = [
    ("President", 1),
    ("Secretary", 2),
    ("Joint Secretary (Programmes)", 3),
    ("Treasurer", 4),
    ("Joint Secretary (Social media, Outreach and Website)", 5),
]


def seed_roles_and_link_assignments(apps, schema_editor):
    Designation = apps.get_model("bandhuapp", "Designation")
    DesignationRole = apps.get_model("bandhuapp", "DesignationRole")
    PeoplesDesignation = apps.get_model("bandhuapp", "PeoplesDesignation")

    for title in ("Office Bearers", "Other"):
        designation = Designation.objects.filter(title=title).first()
        if not designation:
            continue

        role_by_title = {}
        for role_title, rank in OFFICE_BEARER_ROLE_TITLES:
            role, _ = DesignationRole.objects.get_or_create(
                designation=designation,
                title=role_title,
                defaults={"rank": rank},
            )
            if role.rank != rank:
                role.rank = rank
                role.save(update_fields=["rank"])
            role_by_title[role_title] = role

        for assignment in PeoplesDesignation.objects.filter(
            designation=designation
        ).select_related("staff__profile"):
            profile = assignment.staff.profile
            profession = (profile.profession or "").strip()
            if not profession:
                continue

            position = ""
            occupation = profession
            if ", " in profession:
                position, occupation = profession.rsplit(", ", 1)
                position = position.strip()
                occupation = occupation.strip()

            if position:
                role = role_by_title.get(position)
                if not role:
                    role = DesignationRole.objects.create(
                        designation=designation,
                        title=position,
                        rank=assignment.rank or 9999,
                    )
                    role_by_title[position] = role
                assignment.role = role
                if occupation:
                    assignment.desc = occupation
                assignment.save(update_fields=["role", "desc"])
                if occupation and profile.profession != occupation:
                    profile.profession = occupation
                    profile.save(update_fields=["profession"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("bandhuapp", "0014_designation_roles_and_multiple_assignments"),
    ]

    operations = [
        migrations.RunPython(seed_roles_and_link_assignments, noop_reverse),
    ]
