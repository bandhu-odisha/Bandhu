from django.shortcuts import render

from bandhuapp.models import HomePage as SiteHomePage, Mission

from .image_utils import image_field_url, static_image_url
from .models import CarouselImage, HomePage, Product

SWABALAMBAN_HERO_STATIC = 'img/pimg2.jpg'


def _resolve_swabalamban_hero(page, carousel, mission):
    if page and page.picture:
        url = image_field_url(page.picture)
        if url:
            return url
    for row in carousel:
        url = image_field_url(row.picture)
        if url:
            return url
    if mission:
        row = mission.swabalambancarousel_set.first()
        if row:
            url = image_field_url(row.picture)
            if url:
                return url
    return static_image_url(SWABALAMBAN_HERO_STATIC)


def index(request):
    page = HomePage.objects.first()
    mission = Mission.objects.first()
    products = Product.objects.filter(is_published=True).order_by('sort_order', 'name')
    carousel = list(CarouselImage.objects.all().order_by('sort_order', 'id'))

    tagline = ''
    desc = ''
    caption_en = ''
    caption_or = ''
    order_note = ''
    whatsapp_number = ''
    products_heading = 'Quality produce from our Swabalamban initiative.'

    if page:
        tagline = page.tagline or ''
        desc = page.description or ''
        caption_en = page.caption_en or ''
        caption_or = page.caption_or or ''
        order_note = page.order_note or ''
        whatsapp_number = page.whatsapp_number or ''
        products_heading = page.products_heading or products_heading

    if not tagline and mission:
        tagline = mission.swabalamban_tagline or ''
    if not desc and mission:
        desc = mission.swabalamban_desc or ''

    if not caption_en:
        caption_en = '"Self-reliance blossoms when villages shape their own path."'
    if not caption_or:
        caption_or = '"ଗାଁ ନିଜ ପଥ ନିଜେ ଗଢିଲେ ସ୍ୱାବଳମ୍ବନ ଫୁଲିଉଠେ।"'

    ctx = {
        'page_title': 'Swabalamban',
        'tagline': tagline,
        'desc': desc,
        'images': [],
        'content': SiteHomePage.objects.first(),
        'pillar_hero_url': _resolve_swabalamban_hero(page, carousel, mission),
        'products': products,
        'caption_en': caption_en,
        'caption_or': caption_or,
        'order_note': order_note,
        'whatsapp_number': whatsapp_number,
        'products_heading': products_heading,
    }
    return render(request, 'pillar_page.html', ctx)
