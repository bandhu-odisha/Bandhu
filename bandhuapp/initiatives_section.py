"""Homepage “Support a Cause” cards — read from each initiative’s own HomePage."""

from applications.anandakendra.models import HomePage as KendraHomePage
from applications.ankurayan.models import HomePage as AnkurayanHomePage
from applications.ashram.models import HomePage as AshramHomePage
from applications.charitywork.models import HomePage as CharityHomePage
from applications.publications.models import HomePage as PublicationsHomePage


def _card_fields(home_page, file_url):
    if not home_page:
        return {'thumb': None, 'desc': ''}
    desc = (getattr(home_page, 'description', None) or '').strip()
    if not desc:
        desc = (getattr(home_page, 'tagline', None) or '').strip()
    thumb_field = getattr(home_page, 'picture', None)
    return {
        'thumb': file_url(thumb_field),
        'desc': desc,
    }


def build_initiatives_payload(file_url):
    """API shape used by Initiatives.jsx and classic landing_page.html."""
    ankurayan = _card_fields(AnkurayanHomePage.objects.first(), file_url)
    kendra = _card_fields(KendraHomePage.objects.first(), file_url)
    bandhughar = _card_fields(AshramHomePage.objects.first(), file_url)
    other = _card_fields(CharityHomePage.objects.first(), file_url)
    publications = _card_fields(PublicationsHomePage.objects.first(), file_url)

    if not any(
        card['thumb'] or card['desc']
        for card in (ankurayan, kendra, bandhughar, other, publications)
    ):
        return None

    return {
        'ankurayan_thumb': ankurayan['thumb'],
        'ankurayan_desc': ankurayan['desc'],
        'kendra_thumb': kendra['thumb'],
        'kendra_desc': kendra['desc'],
        'bandhughar_thumb': bandhughar['thumb'],
        'bandhughar_desc': bandhughar['desc'],
        'otheract_thumb': other['thumb'],
        'otheract_desc': other['desc'],
        'publications_thumb': publications['thumb'],
        'publications_desc': publications['desc'],
    }
