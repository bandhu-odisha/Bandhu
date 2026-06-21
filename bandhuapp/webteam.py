"""Web team contributors — footer credits and /people/#web-team tab."""

from django.urls import reverse

WEBTEAM_DESIGNATION = 'Web Team'
WEBTEAM_TAB_SLUG = 'web-team'

# GitHub commit counts (dependabot excluded — automated dependency bot).
WEBTEAM_MEMBERS = [
    {
        'first_name': 'Priyansh',
        'last_name': 'Garg',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/priyansh3133/',
        'rank': 1,
    },
    {
        'first_name': 'Aman',
        'last_name': 'Chande',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/aman-chande-544666170/',
        'rank': 2,
    },
    {
        'first_name': 'Heet',
        'last_name': 'Gupta',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/heet-gupta-07366b177/',
        'rank': 3,
    },
    {
        'first_name': 'Brijmohan',
        'last_name': 'Siyag',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/brijsiyag/',
        'rank': 4,
    },
    {
        'first_name': 'Richa',
        'last_name': 'Sawatkar',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/richa-sawatkar-4170a6271/',
        'rank': 5,
    },
    {
        'first_name': 'Aparna',
        'last_name': 'Bhatt',
        'profession': 'Website development',
        'external_url': 'https://www.linkedin.com/in/aparna-bhatt-8bb134215/',
        'rank': 6,
    },
]


def webteam_page_url():
    return reverse('people_page') + f'#{WEBTEAM_TAB_SLUG}'


def _staff_profile_url(first_name, last_name):
    from bandhuapp.models import Staff

    staff = Staff.objects.filter(
        profile__first_name__iexact=first_name,
        profile__last_name__iexact=last_name,
    ).first()
    if not staff:
        return None
    return reverse('staff_profile', kwargs={'id': staff.id})


def webteam_contributors():
    contributors = []
    for member in WEBTEAM_MEMBERS:
        name = f"{member['first_name']} {member['last_name']}"
        url = _staff_profile_url(member['first_name'], member['last_name']) or member['external_url']
        contributors.append({'name': name, 'url': url})
    return contributors


def webteam_footer_context():
    return {
        'webteam_page_url': webteam_page_url(),
        'webteam_contributors': webteam_contributors(),
    }


def webteam_landing_payload():
    return {
        'page_url': webteam_page_url(),
        'contributors': webteam_contributors(),
    }
