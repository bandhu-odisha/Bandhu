from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .forms import AdminAddUserForm, UserAdminChangeForm
from .admin_form_utils import admin_form_with_user
from .models import User

admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances

    form = UserAdminChangeForm
    add_form = AdminAddUserForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_admin','is_active','auth','is_staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'admin_password'),
            'description': (
                'Email is optional. No password is required for the member — they can sign in later via '
                'password reset or set a password when they register. '
                'New members never receive admin access. '
                'If you enter your own admin email, confirm with your password; the member still gets a separate login.'
            ),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            return admin_form_with_user(AdminAddUserForm, request.user)
        return form


admin.site.register(User, UserAdmin)

admin.site.site_header = 'Bandhu'
admin.site.site_title = 'Bandhu Admin Portal'
admin.site.index_title = 'Welome to Bandhu Administration'
