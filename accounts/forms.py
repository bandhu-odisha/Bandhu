from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError

from django.template import loader
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label=None,widget=forms.PasswordInput(attrs={'placeholder':'Password','class':'input100'}))
    password2 = forms.CharField(label=None,widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password','class':'input100'}))
    email = forms.CharField(label=None,widget=forms.EmailInput(attrs={'placeholder':'Email','class':'input100'}))

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

# NEEDED 

class UserAdminCreationForm(forms.ModelForm):
    """Legacy admin user creation with password (unused; see AdminAddUserForm)."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminAddUserForm(forms.Form):
    """Django admin: add members with name and optional email (no password)."""
    first_name = forms.CharField(max_length=150, label='First name')
    last_name = forms.CharField(max_length=150, label='Last name')
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

    def __init__(self, *args, admin_user=None, **kwargs):
        self.admin_user = admin_user
        super().__init__(*args, **kwargs)

    def clean_first_name(self):
        from bandhuapp.helpers import proper_case
        return proper_case(self.cleaned_data['first_name'])

    def clean_last_name(self):
        from bandhuapp.helpers import proper_case
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
        from bandhuapp.admin_forms import create_profile_for_admin_user
        from accounts.admin_helpers import apply_admin_created_user_defaults

        user = User(email=self.cleaned_data['login_email'])
        apply_admin_created_user_defaults(user)
        if commit:
            user.save()
            create_profile_for_admin_user(
                user,
                self.cleaned_data['first_name'].strip(),
                self.cleaned_data['last_name'].strip(),
            )
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin', 'auth', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        # email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            body = loader.render_to_string(html_email_template_name, context)
            # email_message.attach_alternative(html_email, 'text/html')

        # email_message.send()

        email = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=body,
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(email)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)