"""
Seed homepage mission copy and section image paths for local development.
Run: python manage.py seed_landing_content
"""
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from bandhuapp.models import (
    Mission,
    Initiatives,
    SanskarCarousel,
    SwarajCarousel,
    SwabalambanCarousel,
    Contact,
)

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

MISSION_COPY = {
    'sanskar_tagline': 'Anandakendra and Ankurayan',
    'sanskar_desc': SANSKAR_DESC,
    'swaraj_tagline': 'For the common man...',
    'swaraj_desc': (
        'This front of our activities is dedicated to strengthening people\'s participation '
        'in democracy through empowerment and awareness.'
    ),
    'swabalamban_tagline': 'In the village and by the villagers...',
    'swabalamban_desc': (
        'Swabalamban strives to revive the spirit of our villages and check, rather reverse, '
        'the mindless migration to cities. Processing units for farm products like paddy, '
        'cereals, oilseeds are set up in rural areas to ensure the financial stability of '
        'farmers. Youth are assisted to become self-sustainable financially.'
    ),
}

INITIATIVES_COPY = {
    'ankurayan_desc': 'A festival of light and delight for children.... ଆଲୋକ ଓ ଆନନ୍ଦର ଉତ୍ସବ...',
    'kendra_desc': 'Man making initiative of Bandhu... ଏକ ସମ୍ବେଦନଶୀଳ ନୂଆପିଢୀର ନିର୍ମାଣାର୍ଥେ ....',
    'bandhughar_desc': 'An abode for goodness... ବନ୍ଧୁ ମାନଙ୍କ ପାଇଁ ଘରଟିଏ...',
    'otheract_desc': 'We feel so we act... କର୍ମ ଯୋଗୀ ବନ୍ଧୁ.....',
    'publications_desc': 'An outline of changing time... ଆମ ସମୟର ସାମାନ୍ୟ କଥନ.....',
}

CONTACT_DETAILS = {
    'address': 'Village-Lankapara, Po-Lankapara, Jagatsinghapur, Odisha, India, 754134',
    'contact_no': '+91 94374 39371',
    'email': 'bandhuodisha@gmail.com',
    'facebook_link': 'https://www.facebook.com/npobandhu/',
    'twitter_link': '#',
}

PILLAR_IMAGES = {
  'sanskar': ('bandhuapp/sanskar/collage_1_HlxwGsj.jpg', 'collage_1_HlxwGsj.jpg'),
  'swaraj': ('bandhuapp/swaraj/our_mission1.jpg', 'our_mission1.jpg'),
  'swabalamban': ('bandhuapp/swabalamban/swamblamban_1.png', 'swamblamban_1.png'),
}


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
        mission = Mission.objects.first()
        if not mission:
            mission = Mission.objects.create(**MISSION_COPY)
        else:
            for field, value in MISSION_COPY.items():
                setattr(mission, field, value)
            mission.save()

        for pillar, (relative_path, source_name) in PILLAR_IMAGES.items():
            if not self._copy_image(relative_path, source_name):
                continue
            model = {
                'sanskar': SanskarCarousel,
                'swaraj': SwarajCarousel,
                'swabalamban': SwabalambanCarousel,
            }[pillar]
            carousel = model.objects.filter(mission=mission).first()
            if not carousel:
                carousel = model(mission=mission)
            carousel.picture = relative_path
            carousel.save()

        initiatives = Initiatives.objects.first()
        if initiatives:
            for field, value in INITIATIVES_COPY.items():
                setattr(initiatives, field, value)
            initiatives.save()

        contact, _created = Contact.objects.get_or_create(
            pk=1,
            defaults=CONTACT_DETAILS,
        )
        for field, value in CONTACT_DETAILS.items():
            setattr(contact, field, value)
        contact.save()

        self.stdout.write(self.style.SUCCESS('Landing mission and initiatives content updated.'))
