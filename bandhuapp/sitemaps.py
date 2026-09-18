"""Public sitemap: static routes, pillar pages, initiative index pages,
published detail pages, and publications.

Uses `django.contrib.sitemaps` only -- no `django.contrib.sites` app.
`django.contrib.sitemaps.views.sitemap` builds absolute URLs from the
request itself (`get_current_site(request)` falls back to a request-based
`RequestSite` when `django.contrib.sites` isn't installed), so we never need
that migration-bearing app just to publish a sitemap.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    url_names = [
        'home',
        'people_page',
        'pillar_sanskar',
        'pillar_swaraj',
        'ankurayan:ankurayan',
        'anandakendra:anandakendra',
        'ashram:ashram',
        'charitywork:charity_work',
        'publications:index',
        'pillar_swabalamban',
        'prasantaraktadan:prasantaraktadan',
        'patriotism:patriotism',
        'sevavrata:sevavrata',
    ]

    def items(self):
        return self.url_names

    def location(self, item):
        return reverse(item)


class _EntryDetailSitemap(Sitemap):
    """Detail pages for one initiative app's entries (e.g. Bandhughar)."""
    changefreq = 'monthly'
    priority = 0.5
    model = None
    detail_url_name = None
    published_only = False

    def items(self):
        qs = self.model.objects.all().order_by('slug')
        if self.published_only:
            qs = qs.filter(is_published=True)
        return qs

    def location(self, entry):
        return reverse(self.detail_url_name, kwargs={'slug': entry.slug})


def _entry_sitemap(model, detail_url_name, published_only=False):
    return type(
        f'{model.__name__}DetailSitemap',
        (_EntryDetailSitemap,),
        {'model': model, 'detail_url_name': detail_url_name, 'published_only': published_only},
    )


class PublicationsSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        from applications.publications.models import Publication
        return Publication.objects.filter(is_visible=True).order_by('slug')

    def location(self, publication):
        return reverse('publications:publication', kwargs={'slug': publication.slug})

    def lastmod(self, publication):
        return publication.modified


def get_sitemaps():
    """Built lazily (not at import time) so app models are ready when urls.py imports this module."""
    from applications.anandakendra.models import AnandaKendra
    from applications.ashram.models import Ashram
    from applications.charitywork.models import Charity
    from applications.ankurayan.models import Ankurayan
    from applications.patriotism.models import Ashram as PatriotismAshram
    from applications.prasantaraktadan.models import Ashram as PrasantaraktadanAshram
    from applications.sevavrata.models import Ashram as SevavrataAshram

    return {
        'static': StaticViewSitemap,
        'bandhughar': _entry_sitemap(Ashram, 'ashram:AshramDetail'),
        'anandakendra': _entry_sitemap(AnandaKendra, 'anandakendra:AnandkendraDetail'),
        'charitywork': _entry_sitemap(Charity, 'charitywork:CharityDetail'),
        'ankurayan': _entry_sitemap(Ankurayan, 'ankurayan:AnkurayanDetail'),
        'patriotism': _entry_sitemap(PatriotismAshram, 'patriotism:AshramDetail', published_only=True),
        'prasantaraktadan': _entry_sitemap(PrasantaraktadanAshram, 'prasantaraktadan:AshramDetail', published_only=True),
        'sevavrata': _entry_sitemap(SevavrataAshram, 'sevavrata:AshramDetail', published_only=True),
        'publications': PublicationsSitemap,
    }
