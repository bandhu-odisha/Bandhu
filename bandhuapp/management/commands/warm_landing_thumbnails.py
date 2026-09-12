"""
Pre-generate the WebP thumbnails the home page serves (see `responsive_image`
in bandhuapp/helpers.py and THUMBNAIL_ALIASES in bandhu/settings.py), so the
first real visitor after a deploy does not pay generation cost.

Run once after deploying the home page load-time fix, and again after a bulk
media import (e.g. `import_local_media`).

Run: python manage.py warm_landing_thumbnails
"""
from django.core.management.base import BaseCommand

from bandhuapp.helpers import responsive_image
from bandhuapp.models import (
    HeroSlide, HomePage, HomeVisitor, Photo,
    SanskarHomePage, SwabalambanHomePage, SwarajHomePage,
)


class Command(BaseCommand):
    help = 'Pre-generate landing-page WebP thumbnails so visitors never pay generation cost.'

    def handle(self, *args, **options):
        warmed = 0
        skipped = 0

        def warm(field):
            nonlocal warmed, skipped
            if responsive_image(field):
                warmed += 1
            else:
                skipped += 1

        for p in Photo.objects.filter(approved=True):
            warm(p.picture)
        for visitor in HomeVisitor.objects.all():
            warm(visitor.photo)
        for slide in HeroSlide.objects.all():
            warm(slide.image)
        for home in HomePage.objects.all():
            warm(home.banner_image)
        for page_model in (SanskarHomePage, SwarajHomePage, SwabalambanHomePage):
            for page in page_model.objects.all():
                warm(page.hero_image)
                for photo in page.photos.all():
                    warm(photo.picture)

        self.stdout.write(
            self.style.SUCCESS(f'Done. Warmed {warmed} image(s), skipped {skipped}.')
        )
