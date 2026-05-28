from datetime import date
from pathlib import Path
import urllib.request

from django.core.management.base import BaseCommand
from django.conf import settings

from applications.ankurayan.models import Ankurayan, HomePage

ANKURAYAN_INTRO = (
    'ANKURAYAN is a small and sincere effort where we introduce to the young minds '
    'a nobler, happier and more complete ways and points of view of life through '
    'informal sessions and creative events along with conducting various competitions '
    'among school students. Ankurayan 2025 will be celebrated from 17-Dec to 19-Dec-25. '
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


class Command(BaseCommand):
    help = 'Seed Ankurayan homepage intro and year cards from live content.'

    def handle(self, *args, **options):
        homepage = HomePage.objects.first()
        if homepage:
            homepage.tagline = 'Ankurayan'
            homepage.description = ANKURAYAN_INTRO
            homepage.save(update_fields=['tagline', 'description'])

        default_logo = 'ankurayan/logo/Logo.jpg'
        logo_dir = Path(settings.MEDIA_ROOT) / 'ankurayan' / 'logo'
        logo_dir.mkdir(parents=True, exist_ok=True)

        for filename in set(YEAR_LOGOS.values()):
            local_path = logo_dir / filename
            if local_path.exists():
                continue
            try:
                req = urllib.request.Request(
                    f'https://bandhuodisha.in/media/ankurayan/logo/{filename}',
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': 'https://bandhuodisha.in/ankurayan/',
                    },
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    local_path.write_bytes(response.read())
            except Exception:
                pass

        kept_ids = []
        for year, theme in YEAR_THEMES:
            logo_name = YEAR_LOGOS.get(year, 'Logo.jpg')
            logo_field = f'ankurayan/logo/{logo_name}'
            defaults = {
                'title': f'Ankurayan {year}',
                'theme': theme,
                'description': theme,
                'start_date': date(year, 12, 17),
                'end_date': date(year, 12, 19),
                'logo': logo_field,
                'slug': f'ankurayan-{year}',
            }
            ankurayan, _created = Ankurayan.objects.get_or_create(year=year, defaults=defaults)
            ankurayan.title = f'Ankurayan {year}'
            ankurayan.theme = theme
            desc = (ankurayan.description or '').strip()
            if (not desc) or desc.startswith('Imported Ankurayan'):
                ankurayan.description = theme
            ankurayan.slug = f'ankurayan-{year}'
            if (not ankurayan.logo) or ankurayan.logo.name.endswith('Logo.jpg'):
                ankurayan.logo = logo_field if (logo_dir / logo_name).exists() else default_logo
            if not ankurayan.start_date:
                ankurayan.start_date = defaults['start_date']
            if not ankurayan.end_date:
                ankurayan.end_date = defaults['end_date']
            ankurayan.save()
            kept_ids.append(ankurayan.id)

        Ankurayan.objects.exclude(id__in=kept_ids).delete()
        self.stdout.write(self.style.SUCCESS(f'Seeded Ankurayan home content and {len(kept_ids)} year records.'))
