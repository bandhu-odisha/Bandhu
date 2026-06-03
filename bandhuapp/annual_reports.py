"""Serialize annual reports for templates and the landing API."""

ANNUAL_REPORTS_UPLOAD_PATH = '/annual-reports/upload/'


def annual_reports_upload_url():
    """Resolve upload page URL; fallback if URLconf not reloaded yet."""
    try:
        from django.urls import NoReverseMatch, reverse
        return reverse('annual_reports_upload')
    except Exception:
        return ANNUAL_REPORTS_UPLOAD_PATH


def serialize_annual_reports(request):
    from .models import AnnualReport

    items = []
    for report in AnnualReport.objects.filter(is_published=True).order_by('-year'):
        url = report.get_public_url(request)
        if not url:
            continue
        items.append({
            'id': report.pk,
            'year': report.year,
            'title': report.display_title(),
            'url': url,
            'is_external': not bool(report.pdf_file),
        })
    return items


def serialize_annual_reports_admin(request):
    """All reports for the admin upload modal."""
    from .models import AnnualReport

    items = []
    for report in AnnualReport.objects.all().order_by('-year'):
        items.append({
            'id': report.pk,
            'year': report.year,
            'title': report.display_title(),
            'is_published': report.is_published,
            'view_url': report.get_public_url(request),
            'has_pdf': bool(report.pdf_file),
            'external_url': (report.external_url or '').strip(),
        })
    return items


def is_annual_report_ajax(request):
    if request.GET.get('format') == 'json':
        return True
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
