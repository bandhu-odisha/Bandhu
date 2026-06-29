"""Load and render Sanskar / Swaraj / Swabalamban pillar home pages."""

from django.templatetags.static import static

from bandhuapp.helpers import (
    clear_stale_image_field,
    image_field_available,
    image_field_url,
    pillar_gallery_images,
    prune_stale_pillar_photos,
)
from bandhuapp.models import (
    HomePage,
    SanskarHomePage,
    SwabalambanHomePage,
    SwarajHomePage,
)

DEFAULT_SANSKAR_IMAGE_CAPTION_EN = (
    '"Learning with values lights every life and builds a brighter tomorrow."'
)
DEFAULT_SANSKAR_IMAGE_CAPTION_OR = (
    '"ମୂଲ୍ୟ ସହିତ ଶିକ୍ଷା ପ୍ରତ୍ୟେକ ଜୀବନକୁ ଆଲୋକିତ କରେ ଏବଂ ଏକ ଉଜ୍ଜ୍ୱଳ ଭବିଷ୍ୟତ ଗଢେ।"'
)
DEFAULT_SWARAJ_TEXT_CAPTION_EN = (
    '"Empowered communities shape their own future with dignity and voice."'
)
DEFAULT_SWARAJ_TEXT_CAPTION_OR = (
    '"ସଶକ୍ତ ସମୁଦାୟ ଗରିମା ଏବଂ ନିଜ ଅଧିକାର ସହ ନିଜ ଭବିଷ୍ୟତ ଗଢେ।"'
)
DEFAULT_SWABALAMBAN_IMAGE_CAPTION_EN = (
    '"Self-reliance blossoms when villages shape their own path."'
)
DEFAULT_SWABALAMBAN_IMAGE_CAPTION_OR = (
    '"ଗାଁ ନିଜ ପଥ ନିଜେ ଗଢିଲେ ସ୍ୱାବଳମ୍ବନ ଫୁଲିଉଠେ।"'
)


def _hero_from_rows(rows, *, prefer_collage=False):
    for row in rows:
        pic = getattr(row, 'picture', None)
        name = (getattr(pic, 'name', None) or '').lower()
        if prefer_collage and 'collage' in name and image_field_available(pic):
            return pic
    for row in rows:
        pic = getattr(row, 'picture', None)
        if image_field_available(pic):
            return pic
    return None


def _resolve_hero(page, photo_rows, *, prefer_collage=False):
    if page and image_field_available(page.hero_image):
        return page.hero_image
    return _hero_from_rows(photo_rows, prefer_collage=prefer_collage)


def _pillar_hero_assets(page, photo_rows, *, prefer_collage=False, fallback_static='img/our_mission1.jpg'):
    hero_image = _resolve_hero(page, photo_rows, prefer_collage=prefer_collage)
    hero_url = image_field_url(hero_image)
    if hero_url:
        return hero_image, hero_url
    return None, static(fallback_static)


def _prepare_pillar_page(page):
    """Drop stale media paths so missing files are not linked or used as heroes."""
    if page:
        clear_stale_image_field(page, 'hero_image')
        prune_stale_pillar_photos(page.photos.all())
        return list(page.photos.all())
    return []


def build_sanskar_context(*, related_links):
    page = SanskarHomePage.objects.first()
    photo_rows = _prepare_pillar_page(page)
    hero_image, hero_url = _pillar_hero_assets(
        page,
        photo_rows,
        prefer_collage=True,
        fallback_static='img/our_mission.jpg',
    )

    return {
        'page_title': 'Sanskar',
        'tagline': page.tagline if page else '',
        'desc': page.description if page else '',
        'images': pillar_gallery_images(photo_rows, exclude_picture=hero_image),
        'content': HomePage.objects.first(),
        'related_links': related_links,
        'pillar_hero_image': hero_image,
        'pillar_hero_url': hero_url,
        'sanskar_hero_image': hero_image,
        'image_caption_en': (
            (page.image_caption_en if page else '')
            or DEFAULT_SANSKAR_IMAGE_CAPTION_EN
        ),
        'image_caption_or': (
            (page.image_caption_or if page else '')
            or DEFAULT_SANSKAR_IMAGE_CAPTION_OR
        ),
    }


def _swaraj_caption(page, field_name, default):
    if not page:
        return default
    image_value = (getattr(page, f'image_{field_name}', None) or '').strip()
    text_value = (getattr(page, f'text_{field_name}', None) or '').strip()
    return image_value or text_value or default


def build_swaraj_context():
    page = SwarajHomePage.objects.first()
    photo_rows = _prepare_pillar_page(page)
    hero_image, hero_url = _pillar_hero_assets(
        page,
        photo_rows,
        fallback_static='img/our_mission1.jpg',
    )

    return {
        'page_title': 'Swaraj',
        'tagline': page.tagline if page else '',
        'desc': page.description if page else '',
        'images': pillar_gallery_images(photo_rows, exclude_picture=hero_image),
        'content': HomePage.objects.first(),
        'pillar_hero_image': hero_image,
        'pillar_hero_url': hero_url,
        'image_caption_en': _swaraj_caption(page, 'caption_en', DEFAULT_SWARAJ_TEXT_CAPTION_EN),
        'image_caption_or': _swaraj_caption(page, 'caption_or', DEFAULT_SWARAJ_TEXT_CAPTION_OR),
    }


def build_swabalamban_context(*, check_admin=False):
    page = SwabalambanHomePage.objects.first()
    photo_rows = _prepare_pillar_page(page)
    hero_image, hero_url = _pillar_hero_assets(
        page,
        photo_rows,
        fallback_static='img/swamblamban_1.jpg',
    )

    products_heading = 'Quality produce from our Swabalamban initiative.'
    if page:
        products_heading = page.products_heading or products_heading

    return {
        'page_title': 'Swabalamban',
        'tagline': page.tagline if page else '',
        'desc': page.description if page else '',
        'images': pillar_gallery_images(photo_rows, exclude_picture=hero_image),
        'content': HomePage.objects.first(),
        'pillar_hero_image': hero_image,
        'pillar_hero_url': hero_url,
        'caption_en': (
            (page.image_caption_en if page else '')
            or DEFAULT_SWABALAMBAN_IMAGE_CAPTION_EN
        ),
        'caption_or': (
            (page.image_caption_or if page else '')
            or DEFAULT_SWABALAMBAN_IMAGE_CAPTION_OR
        ),
        'order_note': page.order_note if page else '',
        'whatsapp_number': page.whatsapp_number if page else '',
        'products_heading': products_heading,
        'check_admin': check_admin,
    }


def mission_card_payload(file_url):
    """Homepage mission cards: tagline, description snippet, and first image per pillar."""

    def card(page_model, *, prefer_collage=False):
        page = page_model.objects.first()
        rows = _prepare_pillar_page(page)
        hero = _resolve_hero(page, rows, prefer_collage=prefer_collage)
        images = [{'picture': file_url(hero)}] if hero and file_url(hero) else []
        if not images:
            for row in rows:
                url = file_url(getattr(row, 'picture', None))
                if url:
                    images.append({'picture': url})
                    break
        return {
            'tagline': page.tagline if page else '',
            'desc': page.description if page else '',
            'images': images,
        }

    sanskar = card(SanskarHomePage, prefer_collage=True)
    swaraj = card(SwarajHomePage)
    swabalamban = card(SwabalambanHomePage)
    return {
        'sanskar_tagline': sanskar['tagline'],
        'sanskar_desc': sanskar['desc'],
        'sanskar_images': sanskar['images'],
        'swaraj_tagline': swaraj['tagline'],
        'swaraj_desc': swaraj['desc'],
        'swaraj_images': swaraj['images'],
        'swabalamban_tagline': swabalamban['tagline'],
        'swabalamban_desc': swabalamban['desc'],
        'swabalamban_images': swabalamban['images'],
    }
