"""Template context for auth UI (e.g. login modal on all pages)."""


def pop_login_modal_flash(request):
    """Pop one-time login-modal error state from session (call at most once per request)."""
    err = request.session.pop('login_modal_err_code', None)
    if err is None:
        err_code = 0
    else:
        try:
            err_code = int(err)
        except (TypeError, ValueError):
            err_code = 0
    prefill = request.session.pop('login_modal_prefill_email', '') or ''
    return {
        'login_modal_err_code': err_code,
        'login_modal_prefill_email': prefill,
    }


def login_modal(request):
    if getattr(request, '_login_modal_flash_consumed', False):
        return {
            'login_modal_err_code': 0,
            'open_login_modal': request.GET.get('login_modal') == '1',
            'login_modal_prefill_email': '',
        }
    flash = pop_login_modal_flash(request)
    return {
        **flash,
        'open_login_modal': request.GET.get('login_modal') == '1',
    }
