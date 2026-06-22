from datetime import date, datetime
from pathlib import Path
import os
import re
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.ankurayan.guest_examples import EXAMPLE_GUESTS
from applications.ankurayan.models import Ankurayan, Guest, HomePage, Photo

ANKURAYAN_INTRO = (
    'ANKURAYAN is a small and sincere effort where we introduce to the young minds '
    'a nobler, happier and more complete ways and points of view of life through '
    'informal sessions and creative events along with conducting various competitions '
    'among school students.<br>\n'
    '<br>\n'
    'Ankurayan 2025 will be celebrated from 17-Dec to 19-Dec-25.\n'
    '<br>\n'
    'Registration is closed now.'
)

YEAR_THEMES = [
    (2025, 'ସତ୍ୟ-ସାହସ-କରୁଣା-ଶାନ୍ତି ମୋ ଦେଶପ୍ରେମର ଅଭିବ୍ୟକ୍ତି'),
    (2024, 'କଁଅଳ ମନରେ ଓଡ଼ିଆ ଉତଥାନ, ଅଙ୍କୁରାୟନ'),
    (2022, 'Theme of Ankurayan 2022'),
    (2021, 'Theme of Ankurayan 2021'),
    (2020, 'Theme of Ankurayan 2020'),
    (2019, 'Theme of Ankurayan 2019'),
    (2018, 'ଫେରାଇ ଆଣେ ପିଲାପଣ'),
    (2017, 'Theme of Ankurayan 2017'),
    (2016, 'Theme of Ankurayan 2016'),
    (2015, 'Theme of Ankurayan 2015'),
    (2014, 'Theme of Ankurayan 2014'),
    (2013, 'Theme of Ankurayan 2013'),
    (2012, 'Theme of Ankurayan 2012'),
    (2011, 'ପିଲାଟିଏ ଫୁଲଟିଏ'),
]

YEAR_LOGOS = {
    2025: 'Ankurayan_2025_Logo.png',
    2024: 'Ankurayan2024.jpeg',
    2022: 'Ankurayan_22_Logo.jpg',
    2021: 'Logo.jpg',
    2020: 'Ankurayan_2020_Logo_New.jpeg',
    2019: 'Logo2019.jpg',
    2018: 'logo-2018.jpg',
    2017: 'logo2017.jpeg',
    2016: 'Logo2016.jpeg',
    2015: 'Logo2015.jpeg',
    2014: 'Logo2014.jpeg',
    2013: 'Logo2013.jpeg',
    2012: 'Logo2012.jpeg',
    2011: 'logo-_2011.jpeg',
}

YEAR_SCHEDULE = {
    2011: (date(2011, 1, 16), date(2011, 1, 18)),
    2012: (date(2012, 12, 17), date(2012, 12, 19)),
    2013: (date(2013, 12, 17), date(2013, 12, 19)),
    2014: (date(2014, 12, 17), date(2014, 12, 19)),
    2015: (date(2015, 12, 17), date(2015, 12, 20)),
    2016: (date(2016, 12, 16), date(2016, 12, 19)),
    2017: (date(2017, 12, 17), date(2017, 12, 19)),
    2018: (date(2020, 6, 3), date(2020, 6, 9)),
    2019: (date(2020, 6, 2), date(2020, 6, 6)),
    2020: (date(2020, 12, 16), date(2020, 12, 18)),
    2021: (date(2021, 11, 21), date(2021, 12, 19)),
    2022: (date(2022, 11, 23), date(2022, 12, 19)),
    2024: (date(2024, 12, 17), date(2024, 12, 19)),
    2025: (date(2025, 12, 17), date(2025, 12, 19)),
}

FALLBACK_VISITORS = """
<p>Visitors and dignitaries who attended Ankurayan this year shared their experiences:</p>
<ul>
<li><strong>Dr. Meera Patnaik</strong> – Educationist and guest speaker: "The energy and creativity of the participants was inspiring. Bandhu's focus on values and skills together is what our youth need."</li>
<li><strong>Shri Rajesh Kumar</strong> – District official: "A well-organised event that brought villages and towns together. The cultural programmes and competitions reflected true community spirit."</li>
<li><strong>Prof. Anita Das</strong> – University faculty: "Spent the day as a judge for the activities. The level of preparation and the warmth of the volunteers made it a memorable visit."</li>
<li><strong>Parents and guardians</strong> – Many families visited to support participants and expressed gratitude for the platform Ankurayan provides.</li>
</ul>
<p>We thank all visitors for their time and encouragement.</p>
""".strip()

FALLBACK_PUBLICATIONS = """
<p>Publications and media coverage related to this year's Ankurayan:</p>
<ul>
<li><strong>Annual Report – Ankurayan {year}</strong> – Summary of events, participants, and outcomes (available on request).</li>
<li><strong>Photo booklet</strong> – Highlights from the opening ceremony, activities, and prize distribution.</li>
<li><strong>Local press</strong> – Coverage in regional newspapers and community bulletins.</li>
<li><strong>Bandhu newsletter</strong> – A dedicated section in our quarterly newsletter featuring stories and feedback from this Ankurayan.</li>
</ul>
<p>For copies or more information, please contact us.</p>
""".strip()

EXTRA_GUESTS = [
    {
        'name': 'Prof. Anita Das',
        'profession': 'University Faculty',
        'about': 'Spent the day as a judge for the activities. The warmth of the volunteers made it memorable.',
        'quote': (
            'Spent the day as a judge for the activities. '
            'The level of preparation and the warmth of the volunteers made it a memorable visit.'
        ),
        'sort_order': 2,
    },
    {
        'name': 'Suresh Patnaik',
        'profession': 'Community Leader',
        'about': 'Many families visited to support participants. Grateful for the platform Ankurayan provides.',
        'quote': (
            'Many families visited to support participants. '
            'Grateful for the platform Ankurayan provides.'
        ),
        'sort_order': 3,
    },
]

PRODUCTION_BASE = 'https://bandhuodisha.in'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
DJANGO_DUP_SUFFIX = re.compile(r'_[A-Za-z0-9]{7}$')

# Gallery images that production assigns to a year but stores under another folder.
YEAR_GALLERY = {
    2018: ['ankurayan/2020/punchi.jpg'],
    2022: ['ankurayan/2022/Ankuryan-_Titles.png'],
}


def _parse_display_date(value):
    value = value.strip()
    for fmt in ('%d %b, %Y', '%d %B, %Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _extract_schedule_dates(html, year):
    block_match = re.search(r'ankurayan-detail-schedule-dates[\s\S]*?</p>', html, re.I)
    block = block_match.group(0) if block_match else html
    start_match = re.search(r'Starts on\s*<strong>([^<]+)</strong>', block, re.I)
    end_match = re.search(r'Ends on\s*<strong>([^<]+)</strong>', block, re.I)
    start_date = _parse_display_date(start_match.group(1)) if start_match else None
    end_date = _parse_display_date(end_match.group(1)) if end_match else None
    if start_date and end_date:
        return start_date, end_date
    return YEAR_SCHEDULE.get(year, (date(year, 12, 17), date(year, 12, 19)))


def _normalize_media_path(url):
    url = url.split('?', 1)[0]
    if '/media/' in url:
        return url.split('/media/', 1)[1].lstrip('/')
    return url.lstrip('/')


def _prefer_clean_filenames(paths):
    chosen = {}
    for path in paths:
        name = os.path.basename(path)
        stem, ext = os.path.splitext(name)
        clean_stem = DJANGO_DUP_SUFFIX.sub('', stem)
        key = f'{clean_stem.lower()}{ext.lower()}'
        existing = chosen.get(key)
        if existing is None:
            chosen[key] = path
            continue
        existing_stem = os.path.splitext(os.path.basename(existing))[0]
        if '_' in existing_stem and '_' not in stem:
            chosen[key] = path
    return sorted(chosen.values())


def _extract_gallery_paths(html):
    paths = []
    album = re.search(r'djangoAlbumImages\s*=\s*\[(.*?)\];', html, re.S)
    if album:
        paths.extend(_normalize_media_path(src) for src in re.findall(r"src:\s*'([^']+)'", album.group(1)))
    paths.extend(
        _normalize_media_path(src)
        for src in re.findall(r'ankurayan-sidebar-gallery__img[^>]+src="([^"]+)"', html)
    )
    if not paths:
        paths.extend(_normalize_media_path(src) for src in re.findall(r'/media/ankurayan/\d{4}/[^"\']+', html))

    filtered = []
    seen = set()
    for path in paths:
        if '/logo/' in path or '/thumbnails/' in path:
            continue
        if path in seen:
            continue
        seen.add(path)
        filtered.append(path)
    return filtered


def _extract_block(html, pattern):
    match = re.search(pattern, html, re.I | re.S)
    return match.group(1).strip() if match else ''


def _extract_production_fields(html, year):
    description = _extract_block(html, r'id="viewDescription">([\s\S]*?)</div>')
    if not description:
        description = _extract_block(
            html,
            r'id="modalDescription"[\s\S]*?id="viewDescription">([\s\S]*?)</div>',
        )

    visitors = _extract_block(
        html,
        r'class="ankurayan-visitors-intro[^"]*"[^>]*>([\s\S]*?)</div>',
    )
    publications = _extract_block(
        html,
        r'class="ankurayan-publications-intro[^"]*"[^>]*>([\s\S]*?)</div>',
    )

    guests = []
    card_pattern = re.compile(
        r'guest-card-name">([^<]+)</h6>.*?guest-card-profession[^>]*>([^<]+)</p>',
        re.I | re.S,
    )
    quote_pattern = re.compile(r'guest-quote-preview[^>]*>"([^<]+)', re.I)
    for match in card_pattern.finditer(html):
        name = match.group(1).strip()
        profession = match.group(2).strip()
        quote_match = quote_pattern.search(html, match.start(), match.end() + 400)
        quote = ''
        if quote_match:
            quote = quote_match.group(1).strip()
            quote = quote.replace('&#39;', "'").replace('&quot;', '"').replace('…', '...')
        if name:
            guests.append({'name': name, 'profession': profession, 'quote': quote})

    start_date, end_date = _extract_schedule_dates(html, year)

    return {
        'description': description or YEAR_THEMES_DICT.get(year, f'Theme of Ankurayan {year}'),
        'visitors': visitors or FALLBACK_VISITORS,
        'publications': publications or FALLBACK_PUBLICATIONS.format(year=year),
        'guests': guests,
        'start_date': start_date,
        'end_date': end_date,
    }


YEAR_THEMES_DICT = dict(YEAR_THEMES)


class Command(BaseCommand):
    help = 'Seed Ankurayan homepage, year pages, and guest content from live site.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--offline',
            action='store_true',
            help='Do not fetch year-page copy from bandhuodisha.in (use local fallbacks only).',
        )

    def _ensure_media_file(self, relative_path, referer=None):
        destination = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.isfile(destination):
            return True

        basename = os.path.basename(relative_path)
        source = os.path.join(settings.BASE_DIR, 'img', basename)
        if os.path.isfile(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True

        referer = referer or f'{PRODUCTION_BASE}/ankurayan/'
        try:
            request = urllib.request.Request(
                f'{PRODUCTION_BASE}/media/{relative_path}',
                headers={'User-Agent': 'Mozilla/5.0', 'Referer': referer},
            )
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(destination, 'wb') as output_file:
                    output_file.write(response.read())
            return True
        except (urllib.error.URLError, OSError):
            return False

    def _local_year_gallery_paths(self, year):
        year_dir = Path(settings.MEDIA_ROOT) / 'ankurayan' / str(year)
        if not year_dir.is_dir():
            return []
        paths = [
            f'ankurayan/{year}/{path.name}'
            for path in year_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
        return _prefer_clean_filenames(paths)

    def _sync_year_gallery(self, ankurayan, image_paths):
        keep_ids = []
        referer = f'{PRODUCTION_BASE}/ankurayan/detail/{ankurayan.year}/'
        for relative_path in image_paths:
            if not self._ensure_media_file(relative_path, referer=referer):
                self.stdout.write(self.style.WARNING(f'Missing gallery file: {relative_path}'))
                continue

            photo = Photo.objects.filter(ankurayan=ankurayan, picture=relative_path).first()
            if not photo:
                photo = Photo(ankurayan=ankurayan)
            photo.picture.name = relative_path
            photo.approved = True
            photo.save()
            keep_ids.append(photo.id)

        Photo.objects.filter(ankurayan=ankurayan).exclude(id__in=keep_ids).delete()
        return len(keep_ids)

    def _fetch_production_html(self, year):
        url = f'{PRODUCTION_BASE}/ankurayan/detail/{year}/'
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0', 'Referer': f'{PRODUCTION_BASE}/ankurayan/'},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode('utf-8', 'replace')

    def handle(self, *args, **options):
        offline = options['offline']
        picture_path = 'ankurayan/index/Ankurayan_2025_Logo.png'
        banner_path = 'ankurayan/banner/our_mission.jpg'
        for relative_path in (picture_path, banner_path):
            abs_path = Path(settings.MEDIA_ROOT) / relative_path
            if not abs_path.is_file():
                fallback = Path(settings.BASE_DIR) / 'img' / abs_path.name
                if fallback.is_file():
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    abs_path.write_bytes(fallback.read_bytes())

        homepage, _created = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                'tagline': 'Ankurayan',
                'description': ANKURAYAN_INTRO,
                'picture': picture_path,
                'banner_image': banner_path,
            },
        )
        homepage.tagline = 'Ankurayan'
        homepage.description = ANKURAYAN_INTRO
        homepage.picture = picture_path
        if not homepage.banner_image:
            homepage.banner_image = banner_path
        homepage.save()

        default_logo = 'ankurayan/logo/Logo.jpg'
        logo_dir = Path(settings.MEDIA_ROOT) / 'ankurayan' / 'logo'
        logo_dir.mkdir(parents=True, exist_ok=True)

        if not offline:
            for filename in set(YEAR_LOGOS.values()):
                local_path = logo_dir / filename
                if local_path.exists():
                    continue
                try:
                    req = urllib.request.Request(
                        f'{PRODUCTION_BASE}/media/ankurayan/logo/{filename}',
                        headers={
                            'User-Agent': 'Mozilla/5.0',
                            'Referer': f'{PRODUCTION_BASE}/ankurayan/',
                        },
                    )
                    with urllib.request.urlopen(req, timeout=30) as response:
                        local_path.write_bytes(response.read())
                except (urllib.error.URLError, OSError):
                    pass

        kept_ids = []
        synced_years = 0
        guest_created = 0
        photos_synced = 0
        for year, theme in YEAR_THEMES:
            logo_name = YEAR_LOGOS.get(year, 'Logo.jpg')
            logo_field = f'ankurayan/logo/{logo_name}'
            production_fields = None
            html = None
            if not offline:
                try:
                    html = self._fetch_production_html(year)
                    production_fields = _extract_production_fields(html, year)
                    synced_years += 1
                except (urllib.error.URLError, OSError) as exc:
                    self.stdout.write(
                        self.style.WARNING(f'Could not fetch Ankurayan {year} from production: {exc}')
                    )

            if not production_fields:
                fallback_start, fallback_end = YEAR_SCHEDULE.get(
                    year, (date(year, 12, 17), date(year, 12, 19))
                )
                production_fields = {
                    'description': theme,
                    'visitors': FALLBACK_VISITORS,
                    'publications': FALLBACK_PUBLICATIONS.format(year=year),
                    'guests': [],
                    'start_date': fallback_start,
                    'end_date': fallback_end,
                }

            defaults = {
                'title': f'Ankurayan {year}',
                'theme': theme,
                'description': production_fields['description'],
                'visitors': production_fields['visitors'],
                'publications': production_fields['publications'],
                'start_date': production_fields['start_date'],
                'end_date': production_fields['end_date'],
                'logo': logo_field,
                'slug': str(year),
            }
            ankurayan, _created = Ankurayan.objects.get_or_create(year=year, defaults=defaults)
            ankurayan.title = f'Ankurayan {year}'
            ankurayan.theme = theme
            ankurayan.description = production_fields['description']
            ankurayan.visitors = production_fields['visitors']
            ankurayan.publications = production_fields['publications']
            ankurayan.start_date = production_fields['start_date']
            ankurayan.end_date = production_fields['end_date']
            ankurayan.slug = str(year)
            if (not ankurayan.logo) or ankurayan.logo.name.endswith('Logo.jpg'):
                ankurayan.logo = logo_field if (logo_dir / logo_name).exists() else default_logo
            ankurayan.save()
            kept_ids.append(ankurayan.id)

            guest_rows = production_fields['guests'] or [*EXAMPLE_GUESTS, *EXTRA_GUESTS]
            for index, guest in enumerate(guest_rows):
                if Guest.objects.filter(ankurayan=ankurayan, name=guest['name']).exists():
                    continue
                Guest.objects.create(
                    ankurayan=ankurayan,
                    name=guest['name'],
                    profession=guest['profession'],
                    about=guest.get('about') or '',
                    quote=guest.get('quote') or '',
                    email=guest.get('email') or '',
                    contact_no=guest.get('contact_no') or '',
                    facebook_url=guest.get('facebook_url', ''),
                    linkedin_url=guest.get('linkedin_url', ''),
                    sort_order=guest.get('sort_order', index),
                )
                guest_created += 1

            gallery_paths = _extract_gallery_paths(html) if html else []
            if not gallery_paths:
                gallery_paths = YEAR_GALLERY.get(year, [])
            if not gallery_paths:
                gallery_paths = self._local_year_gallery_paths(year)
            photos_synced += self._sync_year_gallery(ankurayan, gallery_paths)

        Ankurayan.objects.exclude(id__in=kept_ids).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded Ankurayan home content, {len(kept_ids)} year records, '
                f'synced {synced_years} year page(s) from production, '
                f'created {guest_created} guest profile(s), '
                f'and synced {photos_synced} gallery photo(s).'
            )
        )
