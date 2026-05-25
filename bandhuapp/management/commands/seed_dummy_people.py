"""
Create two labelled dummy staff profiles for testing People / designations.

Run: python manage.py seed_dummy_people
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bandhuapp.models import Designation, DesignationRole, PeoplesDesignation, Profile, Staff

User = get_user_model()

DUMMY_PASSWORD = "changeme123"

DUMMY_PROFILE_DEFAULTS = {
    "dob": date(1990, 6, 15),
    "contact_no": "9999900001",
    "street_address1": "Dummy Test Address",
    "street_address2": "",
    "city": "Bhubaneswar",
    "state": "Odisha",
    "pincode": "751001",
}

# Person A: Core Team only (no office bearer role)
DUMMY_CORE_ONLY = {
    "email": "demo.core@bandhu.demo",
    "first_name": "Demo",
    "last_name": "CoreOnly",
    "gender": "M",
    "profession": "Volunteer coordinator (dummy)",
    "about": "Dummy profile — appears under Core Team tab only.",
    "designations": ["Core Team"],
    "rank": 99,
}

# Person B: Core Team + Office Bearers with Secretary role
DUMMY_DUAL = {
    "email": "demo.dual@bandhu.demo",
    "first_name": "Demo",
    "last_name": "DualRole",
    "gender": "F",
    "profession": "Software developer (dummy)",
    "about": "Dummy profile — Core Team and Office Bearers (Secretary).",
    "assignments": [
        {"designation": "Core Team", "rank": 98, "role": None, "desc": "Tech volunteer (dummy)"},
        {
            "designation": "Office Bearers",
            "rank": 98,
            "role": "Secretary",
            "desc": "Faculty member (dummy)",
        },
    ],
}


class Command(BaseCommand):
    help = "Creates two dummy staff profiles for testing People page and designations."

    def handle(self, *args, **options):
        core_team = Designation.objects.filter(title="Core Team").first()
        office_bearers = Designation.objects.filter(title="Office Bearers").first()
        if not core_team or not office_bearers:
            self.stderr.write(
                self.style.ERROR(
                    "Run `python manage.py seed_people` first to create designations."
                )
            )
            return

        roles = {}
        if office_bearers:
            for role in DesignationRole.objects.filter(designation=office_bearers):
                roles[role.title] = role

        self._seed_core_only(DUMMY_CORE_ONLY, core_team)
        self._seed_dual(DUMMY_DUAL, core_team, office_bearers, roles)

        self.stdout.write(self.style.SUCCESS("\nDummy profiles ready:\n"))
        self.stdout.write("  1. Demo CoreOnly  — Core Team only")
        self.stdout.write("     Email: demo.core@bandhu.demo")
        self.stdout.write("  2. Demo DualRole  — Core Team + Office Bearers (Secretary)")
        self.stdout.write("     Email: demo.dual@bandhu.demo")
        self.stdout.write(f"\n  Password (both): {DUMMY_PASSWORD}")
        self.stdout.write("\n  View: /people  |  Edit: Django admin -> Staff\n")

    def _ensure_user_profile_staff(self, spec):
        user, created = User.objects.get_or_create(email=spec["email"])
        if created:
            user.set_password(DUMMY_PASSWORD)
            user.is_active = True
            user.save()

        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
                "gender": spec["gender"],
                "profession": spec["profession"],
                **DUMMY_PROFILE_DEFAULTS,
            },
        )
        profile.first_name = spec["first_name"]
        profile.last_name = spec["last_name"]
        profile.gender = spec["gender"]
        profile.profession = spec["profession"]
        for key, value in DUMMY_PROFILE_DEFAULTS.items():
            setattr(profile, key, value)
        profile.save()

        staff, _ = Staff.objects.get_or_create(
            profile=profile,
            defaults={"about": spec["about"]},
        )
        staff.about = spec["about"]
        staff.save(update_fields=["about"])
        return staff

    def _seed_core_only(self, spec, core_team):
        staff = self._ensure_user_profile_staff(spec)
        pd, _ = PeoplesDesignation.objects.update_or_create(
            staff=staff,
            designation=core_team,
            role=None,
            defaults={"desc": spec["profession"], "rank": spec["rank"]},
        )
        self.stdout.write(f"  Updated {pd}")

    def _seed_dual(self, spec, core_team, office_bearers, roles):
        staff = self._ensure_user_profile_staff(spec)
        designation_map = {
            "Core Team": core_team,
            "Office Bearers": office_bearers,
        }
        for item in spec["assignments"]:
            designation = designation_map[item["designation"]]
            role = roles.get(item["role"]) if item.get("role") else None
            pd, _ = PeoplesDesignation.objects.update_or_create(
                staff=staff,
                designation=designation,
                role=role,
                defaults={
                    "desc": item["desc"],
                    "rank": item["rank"],
                },
            )
            self.stdout.write(f"  Updated {pd}")
