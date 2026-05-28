"""Helpers for wiring admin add-user forms with the current admin account."""


def admin_form_with_user(form_class, admin_user):
    """Return a form class that receives ``admin_user`` from Django admin."""

    class FormWithAdminUser(form_class):
        def __init__(self, *args, **kwargs):
            kwargs['admin_user'] = admin_user
            super().__init__(*args, **kwargs)

    FormWithAdminUser.__name__ = form_class.__name__
    FormWithAdminUser.__module__ = form_class.__module__
    return FormWithAdminUser
