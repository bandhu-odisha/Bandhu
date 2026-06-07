from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from bandhuapp.models import HomePage as SiteHomePage, Mission
from bandhuapp.templatetags.permissions import is_admin

from .image_utils import image_field_url, static_image_url
from .models import CarouselImage, HomePage, Product

SWABALAMBAN_HERO_STATIC = 'img/swamblamban_1.png'


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
        'check_admin': is_admin(request.user),
    }
    return render(request, 'pillar_page.html', ctx)


@login_required
def create_product(request):
    if not is_admin(request.user):
        return redirect('pillar_swabalamban')
    if request.method != 'POST':
        return redirect('pillar_swabalamban')

    name = (request.POST.get('name') or '').strip()
    label = (request.POST.get('label') or name).strip()
    intro_lead = (request.POST.get('intro_lead') or '').strip()
    intro_text = (request.POST.get('intro_text') or '').strip()
    nutritional_highlights = (request.POST.get('nutritional_highlights') or '').strip()
    quality_promise = (request.POST.get('quality_promise') or '').strip()
    image = request.FILES.get('image')

    if not name or not label or not intro_text or not image:
        messages.error(request, 'Product name, label, description, and image are required.')
        return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')

    if Product.objects.filter(name__iexact=name).exists():
        messages.warning(request, f'A product named "{name}" already exists.')
        return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')

    next_sort = (
        Product.objects.order_by('-sort_order').values_list('sort_order', flat=True).first() or 0
    ) + 1
    Product.objects.create(
        name=name,
        label=label,
        image=image,
        intro_lead=intro_lead,
        intro_text=intro_text,
        nutritional_highlights=nutritional_highlights,
        quality_promise=quality_promise,
        sort_order=next_sort,
        is_published=True,
    )
    messages.success(request, f'Product "{name}" added.')
    return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')
