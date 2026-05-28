from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from accounts.models import User

from .helpers import proper_case
from .models import (
    Designation,
    DesignationRole,
    PeoplesDesignation,
    Profile,
    StaffExperience,
    StaffExperiencePhoto,
)


class ProperCaseTitleForm(forms.ModelForm):
    """Capitalise the first letter of each word in title fields (e.g. Office Bearers)."""

    def clean_title(self):
        return proper_case(self.cleaned_data.get('title', ''))


class DesignationAdminForm(ProperCaseTitleForm):
    class Meta:
        model = Designation
        fields = ('title', 'rank')


class DesignationRoleAdminForm(ProperCaseTitleForm):
    class Meta:
        model = DesignationRole
        fields = ('designation', 'title', 'rank')

# Placeholder address/contact for profiles created by admin (member fills in later).
ADMIN_PROFILE_DEFAULTS = {
    'gender': 'M',
    'dob': date(1980, 1, 1),
    'contact_no': '9000000000',
    'street_address1': 'Bandhu Office',
    'street_address2': '',
    'city': 'Jagatsinghpur',
    'state': 'Odisha',
    'pincode': '754134',
    'profession': '',
}


def create_profile_for_admin_user(user, first_name, last_name):
    """Create or update a minimal profile for an admin-added user."""
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            **ADMIN_PROFILE_DEFAULTS,
        },
    )
    if not created:
        profile.first_name = first_name
        profile.last_name = last_name
        profile.save(update_fields=['first_name', 'last_name'])
    return profile


class AdminAddProfileForm(forms.ModelForm):
    """Django admin: add a profile with name and optional email only."""
    email = forms.EmailField(
        required=False,
        label='Email (optional)',
        help_text=(
            'Leave blank if the member has no email. '
            'If you enter your own admin email, confirm with your password below — '
            'the member still gets a separate login and never admin access.'
        ),
    )
    admin_password = forms.CharField(
        required=False,
        label='Your admin password',
        widget=forms.PasswordInput,
        help_text='Required only when you enter an email address that belongs to your admin account.',
    )

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')

    def __init__(self, *args, admin_user=None, **kwargs):
        self.admin_user = admin_user
        super().__init__(*args, **kwargs)

    def clean_first_name(self):
        return proper_case(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return proper_case(self.cleaned_data['last_name'])

    def clean_email(self):
        from accounts.admin_helpers import normalize_admin_add_email
        return normalize_admin_add_email(self.cleaned_data.get('email', ''))

    def clean(self):
        from accounts.admin_helpers import resolve_admin_created_user_email

        cleaned = super().clean()
        if self.errors:
            return cleaned

        try:
            cleaned['login_email'] = resolve_admin_created_user_email(
                entered_email=cleaned.get('email', ''),
                admin_user=self.admin_user,
                admin_password=cleaned.get('admin_password', ''),
                first_name=cleaned.get('first_name', ''),
                last_name=cleaned.get('last_name', ''),
            )
        except ValidationError as exc:
            message = exc.messages[0] if exc.messages else str(exc)
            if exc.code in ('admin_password_required', 'admin_password_invalid'):
                self.add_error('admin_password', message)
            else:
                self.add_error('email', message)
        return cleaned

    def save(self, commit=True):
        from accounts.admin_helpers import apply_admin_created_user_defaults

        user = User(email=self.cleaned_data['login_email'])
        apply_admin_created_user_defaults(user)
        user.save()

        profile = super().save(commit=False)
        profile.user = user
        for key, value in ADMIN_PROFILE_DEFAULTS.items():
            setattr(profile, key, value)
        if commit:
            profile.save()
        return profile

class RoleSelect(forms.Select):
    """Role options carry data-designation-id for admin JS filtering."""

    def __init__(self, *args, role_designation_map=None, **kwargs):
        self.role_designation_map = role_designation_map or {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        if value:
            try:
                designation_id = self.role_designation_map.get(int(value))
            except (TypeError, ValueError):
                designation_id = None
            if designation_id is not None:
                option.setdefault("attrs", {})
                option["attrs"]["data-designation-id"] = str(designation_id)
        return option


class PeoplesDesignationAdminForm(forms.ModelForm):
    class Meta:
        model = PeoplesDesignation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role_map = {
            row["id"]: row["designation_id"]
            for row in DesignationRole.objects.values("id", "designation_id")
        }
        designation_id = self._designation_id_from_form()
        role_qs = DesignationRole.objects.select_related("designation").order_by(
            "designation__rank", "rank", "title"
        )
        if designation_id:
            role_qs = role_qs.filter(designation_id=designation_id)

        role_field = self.fields["role"]
        role_field.queryset = role_qs
        role_widget = RoleSelect(role_designation_map=role_map)
        role_widget.choices = role_field.choices
        role_field.widget = role_widget
        role_field.help_text = (
            "Leave blank for Core Team. For Office Bearers, choose a position "
            "(President, Secretary, Treasurer, etc.)."
        )

    def _designation_id_from_form(self):
        if self.data:
            prefix = self.prefix + "-" if self.prefix else ""
            raw = self.data.get(f"{prefix}designation") or self.data.get("designation")
            if raw:
                return raw
        if self.instance.designation_id:
            return self.instance.designation_id
        return None

    def clean(self):
        cleaned = super().clean()
        designation = cleaned.get("designation")
        role = cleaned.get("role")
        if not designation:
            return cleaned
        if designation.title == "Core Team":
            cleaned["role"] = None
            return cleaned
        if role and role.designation_id != designation.pk:
            self.add_error(
                "role",
                "This role belongs to a different designation. "
                "Choose Office Bearers as the designation, or clear Role.",
            )
        return cleaned


class PeoplesDesignationInlineFormSet(forms.BaseInlineFormSet):
    """Core Team once; multiple Office Bearers rows allowed (different roles)."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        core_team_rows = 0
        seen_keys = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            designation = form.cleaned_data.get("designation")
            if not designation:
                continue
            role = form.cleaned_data.get("role")
            title = designation.title

            if title == "Core Team":
                core_team_rows += 1
                if core_team_rows > 1:
                    raise ValidationError("Only one Core Team row per person (Role empty).")
                key = (designation.pk, None)
            elif title in ("Office Bearers", "Other"):
                if not role:
                    raise ValidationError(
                        "Each Office Bearers row needs a position (President, Secretary, etc.)."
                    )
                key = (designation.pk, role.pk)
            else:
                key = (designation.pk, role.pk if role else None)

            if key in seen_keys:
                if title in ("Office Bearers", "Other") and role:
                    raise ValidationError(
                        f"You added “{role.title}” twice. Pick a different position "
                        f"for each Office Bearers row."
                    )
                raise ValidationError(
                    f"Duplicate “{title}” row on this form."
                )
            seen_keys.add(key)


def _save_experience_photo(experience, image, caption=""):
    """Attach an uploaded image to a staff experience."""
    if not image:
        return
    StaffExperiencePhoto.objects.create(
        experience=experience,
        image=image,
        caption=(caption or "").strip(),
    )


class StaffExperienceInlineForm(forms.ModelForm):
    """Staff admin inline: optional photo upload per experience."""

    image = forms.ImageField(
        required=False,
        label="Photo",
        help_text="Optional image for this experience.",
    )
    image_caption = forms.CharField(
        required=False,
        max_length=255,
        label="Photo caption",
        help_text="Optional caption for the photo above.",
    )

    class Meta:
        model = StaffExperience
        fields = ("message",)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        _save_experience_photo(
            instance,
            self.cleaned_data.get("image"),
            self.cleaned_data.get("image_caption"),
        )
        return instance


class StaffExperienceAdminForm(forms.ModelForm):
    """Standalone staff experience admin: optional photo on create/edit."""

    image = forms.ImageField(
        required=False,
        label="Add photo",
        help_text="Upload an image for this experience (you can add more below).",
    )
    image_caption = forms.CharField(
        required=False,
        max_length=255,
        label="Photo caption",
    )

    class Meta:
        model = StaffExperience
        fields = ("staff", "message")

    def save(self, commit=True):
        instance = super().save(commit=commit)
        _save_experience_photo(
            instance,
            self.cleaned_data.get("image"),
            self.cleaned_data.get("image_caption"),
        )
        return instance
