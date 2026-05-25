"""Resolve notice-board URLs to on-site paths (year-specific Ankurayan, etc.)."""
import re
from urllib.parse import urlparse

from django.urls import reverse

from applications.ankurayan.models import Ankurayan

_YEAR_RE = re.compile(r'\b(20[12]\d)\b')
_LEGACY_HOST = 'bandhuodisha.in'
_ANKURAYAN_LIST_SUFFIXES = ('/ankurayan', '/ankurayan/')


def _extract_year(text):
    if not text:
        return None
    match = _YEAR_RE.search(text)
    return int(match.group(1)) if match else None


def _path_only(url):
    if not url:
        return ''
    parsed = urlparse(url.strip())
    if parsed.scheme in ('http', 'https'):
        return parsed.path or '/'
    return url.strip().split('?', 1)[0]


def _is_generic_ankurayan_list(url):
    path = _path_only(url).rstrip('/') or '/'
    if path in ('/ankurayan',):
        return True
    parsed = urlparse(url.strip()) if url else None
    if parsed and parsed.netloc.replace('www.', '') == _LEGACY_HOST:
        legacy = (parsed.path or '/').rstrip('/') or '/'
        return legacy == '/ankurayan'
    return False


def _ankurayan_detail_path(year):
    slug = f'ankurayan-{year}'
    if Ankurayan.objects.filter(slug=slug).exists():
        return reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug})
    return reverse('ankurayan:ankurayan')


def _rewrite_legacy_site_path(url):
    parsed = urlparse(url.strip())
    if parsed.netloc.replace('www.', '') != _LEGACY_HOST:
        return None
    path = parsed.path or '/'
    if path.rstrip('/') == '/ankurayan':
        return None
    if path.rstrip('/') == '/other_activities':
        return reverse('charitywork:charity_work')
    if path in ('/', ''):
        return '/'
    return path + (f'?{parsed.query}' if parsed.query else '')


def resolve_notice_url(text, url=None):
    """
    Return a same-site path or external URL suitable for notice-board links.
    Rewrites legacy bandhuodisha.in/ankurayan/ list URLs to year detail pages when possible.
    """
    raw = (url or '').strip()
    if not raw or raw == '#':
        return raw or None

    legacy_path = _rewrite_legacy_site_path(raw)
    if legacy_path is not None:
        return legacy_path

    combined = f'{text or ""} {raw}'
    year = _extract_year(combined)
    mentions_ankurayan = bool(re.search(r'ankurayan', combined, re.I))

    if mentions_ankurayan and year and _is_generic_ankurayan_list(raw):
        return _ankurayan_detail_path(year)

    if _is_generic_ankurayan_list(raw):
        if year:
            return _ankurayan_detail_path(year)
        return reverse('ankurayan:ankurayan')

    if raw.startswith('/'):
        return raw
    if raw.startswith('http://') or raw.startswith('https://'):
        return raw
    return raw
