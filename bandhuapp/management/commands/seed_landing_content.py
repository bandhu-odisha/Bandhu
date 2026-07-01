"""
Seed homepage mission copy and section image paths for local development.
Run: python manage.py seed_landing_content
"""
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from bandhuapp.models import (
    SanskarHomePage,
    SanskarHomePhoto,
    SwarajHomePage,
    SwarajHomePhoto,
    SwabalambanHomePage,
    SwabalambanHomePhoto,
    Contact,
    HeroSlide,
    HomePage,
    AboutUs,
    AboutSlide,
)
from applications.ankurayan.models import HomePage as AnkurayanHomePage
from applications.anandakendra.models import HomePage as KendraHomePage
from applications.ashram.models import HomePage as AshramHomePage
from applications.charitywork.models import HomePage as CharityHomePage
from applications.publications.models import HomePage as PublicationsHomePage

IMG_ROOT = os.path.join(settings.BASE_DIR, 'img')
MEDIA_ROOT = settings.MEDIA_ROOT

SANSKAR_DESC = (
    '<b>Anandakendra: </b>Anandakendra is conceived to support the children in '
    'villages for completing their school education successfully. Successfully, not only in '
    'terms of good marks in the examinations but also in terms of a sound understanding of '
    'fundamentals. More importantly, this initiative aims to ensure a supportive environment '
    'for an overall (personal-social-spiritual) development at a tender stage of life. We hope '
    'them to develop in themselves a keen fellow-feeling, a broader, deeper, and more practical '
    'outlook towards life, and a sincere urge to serve.  Anandakendra is not meant to be the '
    'replacement of a school but to take care of the children beyond the school hours.  '
    '<br>\n'
    '<b>Ankurayan: </b>Conceived as an annual festival of light and delight, it has '
    'been organised since 2006 and has now become a household name in some parts of coastal '
    'Odisha. This witnesses a gathering of more than 2000 students each year in mid-December at '
    'the bank of Paika, a distributary of Mahanadi separating the two districts-  Kendrapara and  '
    'Jagatsinghpur.'
)

PILLAR_COPY = {
    'sanskar': {
        'tagline': 'Anandakendra and Ankurayan',
        'description': SANSKAR_DESC,
    },
    'swaraj': {
        'tagline': 'For the common man...',
        'description': (
            'This front of our activities is dedicated to strengthening people\'s participation '
            'in democracy through empowerment and awareness.'
        ),
    },
    'swabalamban': {
        'tagline': 'In the village and by the villagers...',
        'description': (
            'Swabalamban strives to revive the spirit of our villages and check, rather reverse, '
            'the mindless migration to cities. Processing units for farm products like paddy, '
            'cereals, oilseeds are set up in rural areas to ensure the financial stability of '
            'farmers. Youth are assisted to become self-sustainable financially.'
        ),
    },
}

INITIATIVES_COPY = {
    'ankurayan': {
        'tagline': 'A festival of light and delight for children.... ଆଲୋକ ଓ ଆନନ୍ଦର ଉତ୍ସବ...',
        'image': ('main_page/initiatives/ankurayan.jpg', 'ankurayan.jpg'),
    },
    'kendra': {
        'tagline': 'Man making initiative of Bandhu... ଏକ ସମ୍ବେଦନଶୀଳ ନୂଆପିଢୀର ନିର୍ମାଣାର୍ଥେ ....',
        'image': ('main_page/initiatives/anandakendra.jpg', 'anandakendra.jpg'),
    },
    'bandhughar': {
        'tagline': 'An abode for goodness... ବନ୍ଧୁ ମାନଙ୍କ ପାଇଁ ଘରଟିଏ...',
        'image': ('main_page/initiatives/bandhughar.jpg', 'bandhughar.jpg'),
    },
    'otheract': {
        'tagline': 'We feel so we act... କର୍ମ ଯୋଗୀ ବନ୍ଧୁ.....',
        'image': ('main_page/initiatives/other_activities.jpg', 'other_activities.jpg'),
    },
    'publications': {
        'tagline': 'An outline of changing time... ଆମ ସମୟର ସାମାନ୍ୟ କଥନ.....',
        'image': ('main_page/initiatives/publications.jpg', 'publications.jpg'),
    },
}

CONTACT_DETAILS = {
    'address': 'Village-Lankapara, Po-Lankapara, Jagatsinghapur, Odisha, India, 754134',
    'contact_no': '+91 94374 39371',
    'email': 'bandhuodisha@gmail.com',
    'facebook_link': 'https://www.facebook.com/npobandhu/',
    'twitter_link': '#',
}

PILLAR_IMAGES = {
  'sanskar': ('bandhuapp/sanskar/collage_1.jpg', 'collage_1.jpg'),
  'swaraj': ('bandhuapp/swaraj/our_mission1.jpg', 'our_mission1.jpg'),
  'swabalamban': ('bandhuapp/swabalamban/swamblamban_1.jpg', 'swamblamban_1.jpg'),
}

HERO_SLIDES_COPY = [
    {
        'title': 'The Friend of the Last Man',
        'subtitle': (
            'Bandhu is an idea that celebrates goodness — in you, me, and all others. '
            'Friendship, sincerity, and small acts that matter.'
        ),
    },
    {
        'title': 'Goodness in Every Direction',
        'subtitle': (
            'We are people who care about what is inconsistent within and without — and who '
            'choose to do small things with the highest sincerity.'
        ),
    },
    {
        'title': 'Bandhu at twilight',
        'subtitle': (
            'The campus quiets into evening — lights in the windows, trees and lawn in the '
            'half-light, and the place we share still welcoming under the open sky.'
        ),
    },
    {
        'title': 'Life in Bloom',
        'subtitle': (
            'Like the gardens we tend, our work grows with patience, colour, and hope — '
            'together in Odisha and beyond.'
        ),
    },
]

HERO_SLIDE_IMAGES = [
    ('bandhuapp/hero/slide-1.jpg', 'our_mission.jpg'),
    ('bandhuapp/hero/slide-2.jpg', 'our_mission1.jpg'),
    ('bandhuapp/hero/slide-3.jpg', 'about-slide-3-campus.png'),
    ('bandhuapp/hero/slide-4.jpg', 'about-slide-2-hibiscus.png'),
]

ABOUT_COPY = {
    'tagline': (
        'Bandhu is an idea that celebrates goodness, that is in you, me and all others.'
    ),
    'desc': (
        'We are a group of people, good but not necessarily great, with a spontaneous '
        'flow of boundless friendship. The concern is about the inconsistencies within '
        'and without. Bandhu does small things with the highest possible sincerity.'
    ),
}

ABOUT_SLIDES_COPY = [
    {
        'caption': (
            'A gardenia in full bloom—quiet growth, care for the soil, and our bond '
            'with the living world.'
        ),
        'image': ('bandhuapp/about/slide-1-gardenia.png', 'about-slide-1-gardenia.png'),
    },
    {
        'caption': (
            'Double hibiscus in our garden: vivid colour, steady hands, and the joy '
            'we find in nurturing life.'
        ),
        'image': ('bandhuapp/about/slide-2-hibiscus.png', 'about-slide-2-hibiscus.png'),
    },
    {
        'caption': (
            'Bandhu at twilight—where day’s work meets rest, and our community gathers '
            'under an open sky.'
        ),
        'image': ('bandhuapp/about/slide-3-campus.png', 'about-slide-3-campus.png'),
    },
    {
        'caption': (
            'Ixora in bloom: many small flowers, one shared canopy—strength in togetherness.'
        ),
        'image': ('bandhuapp/about/slide-4-ixora.png', 'about-slide-4-ixora.png'),
    },
    {
        'caption': (
            'A full set of blossoms in the green — yellow bells among the vines and leaves, '
            'bright in the thicket.'
        ),
        'image': ('bandhuapp/about/slide-5-blossoms.png', 'about-slide-blossoms.png'),
    },
]


class Command(BaseCommand):
    help = 'Seeds mission copy and pillar image paths for the landing page.'

    def _copy_image(self, relative_path, source_name):
        dest = os.path.join(MEDIA_ROOT, relative_path)
        if os.path.isfile(dest):
            return True

        search_roots = (
            os.path.join(IMG_ROOT, source_name),
            os.path.join(settings.BASE_DIR, 'static', 'img', source_name),
            os.path.join(MEDIA_ROOT, relative_path),
            os.path.join(MEDIA_ROOT, os.path.dirname(relative_path), source_name),
        )
        src = next((path for path in search_roots if os.path.isfile(path)), None)
        if not src:
            self.stdout.write(self.style.WARNING(f'Missing source image: {source_name}'))
            return False
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        return True

    def handle(self, *args, **options):
        page_models = {
            'sanskar': (SanskarHomePage, SanskarHomePhoto),
            'swaraj': (SwarajHomePage, SwarajHomePhoto),
            'swabalamban': (SwabalambanHomePage, SwabalambanHomePhoto),
        }

        for pillar, (relative_path, source_name) in PILLAR_IMAGES.items():
            if not self._copy_image(relative_path, source_name):
                continue
            page_model, photo_model = page_models[pillar]
            copy = PILLAR_COPY[pillar]
            page = page_model.objects.first()
            if not page:
                page = page_model.objects.create(
                    tagline=copy['tagline'],
                    description=copy['description'],
                )
            else:
                page.tagline = copy['tagline']
                page.description = copy['description']
                page.save()
            if not page.hero_image:
                page.hero_image = relative_path
                page.save(update_fields=['hero_image'])
            if not photo_model.objects.filter(page=page).exists():
                photo_model.objects.create(page=page, picture=relative_path, sort_order=0)

        for slide_index, copy in enumerate(HERO_SLIDES_COPY):
            relative_path, source_name = HERO_SLIDE_IMAGES[slide_index]
            if self._copy_image(relative_path, source_name):
                slide = HeroSlide.objects.filter(sort_order=slide_index).first()
                if not slide:
                    slide = HeroSlide(sort_order=slide_index)
                slide.title = copy['title']
                slide.subtitle = copy['subtitle']
                slide.image = relative_path
                slide.save()

        first_hero_image = HERO_SLIDE_IMAGES[0][0]
        homepage = HomePage.objects.first()
        if not homepage:
            if os.path.isfile(os.path.join(MEDIA_ROOT, first_hero_image)):
                HomePage.objects.create(banner_image=first_hero_image, visitors_count=0)
        elif not homepage.banner_image and os.path.isfile(os.path.join(MEDIA_ROOT, first_hero_image)):
            homepage.banner_image = first_hero_image
            homepage.save(update_fields=['banner_image'])

        about = AboutUs.objects.first()
        if not about:
            about = AboutUs.objects.create(**ABOUT_COPY)
        else:
            for field, value in ABOUT_COPY.items():
                setattr(about, field, value)
            about.save()

        for slide_index, copy in enumerate(ABOUT_SLIDES_COPY):
            relative_path, source_name = copy['image']
            if not self._copy_image(relative_path, source_name):
                continue
            slide = AboutSlide.objects.filter(sort_order=slide_index).first()
            if not slide:
                slide = AboutSlide(sort_order=slide_index)
            slide.caption = copy['caption']
            slide.image = relative_path
            slide.save()

        initiative_models = {
            'ankurayan': AnkurayanHomePage,
            'kendra': KendraHomePage,
            'bandhughar': AshramHomePage,
            'otheract': CharityHomePage,
            'publications': PublicationsHomePage,
        }
        for key, page_model in initiative_models.items():
            copy = INITIATIVES_COPY[key]
            relative_path, source_name = copy['image']
            page = page_model.objects.first()
            if not page:
                page = page_model.objects.create(tagline=copy['tagline'])
            else:
                page.tagline = copy['tagline']
                page.save(update_fields=['tagline'])
            if self._copy_image(relative_path, source_name):
                if not page.picture or not page.picture.name:
                    page.picture = relative_path
                    page.save(update_fields=['picture'])

        contact, _created = Contact.objects.get_or_create(
            pk=1,
            defaults=CONTACT_DETAILS,
        )
        for field, value in CONTACT_DETAILS.items():
            setattr(contact, field, value)
        contact.save()

        self.stdout.write(self.style.SUCCESS(
            'Landing mission, hero slides, about section, and initiatives content updated.'
        ))
