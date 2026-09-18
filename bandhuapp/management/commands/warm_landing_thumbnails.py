"""
Pre-generate the WebP thumbnails the home page AND inner pages serve (see
`responsive_image` in bandhuapp/helpers.py, the `{% responsive_img %}`
template tag in bandhuapp/templatetags/responsive_images.py, and
THUMBNAIL_ALIASES in bandhu/settings.py), so the first real visitor after a
deploy does not pay generation cost.

Run once after deploying, and again after a bulk media import (e.g.
`import_local_media`).

Run: python manage.py warm_landing_thumbnails
"""
from django.core.management.base import BaseCommand

from bandhuapp.helpers import responsive_image
from bandhuapp.models import (
    HeroSlide, HomePage, HomeVisitor, Photo, Profile,
    SanskarHomePage, SwabalambanHomePage, SwarajHomePage,
)


class Command(BaseCommand):
    help = 'Pre-generate landing + inner-page WebP thumbnails so visitors never pay generation cost.'

    def handle(self, *args, **options):
        self.warmed = 0
        self.skipped = 0

        # Landing page
        for p in Photo.objects.filter(approved=True):
            self.warm(p.picture)
        for visitor in HomeVisitor.objects.all():
            self.warm(visitor.photo)
        for slide in HeroSlide.objects.all():
            self.warm(slide.image)
        for home in HomePage.objects.all():
            self.warm(home.banner_image)
        for page_model in (SanskarHomePage, SwarajHomePage, SwabalambanHomePage):
            for page in page_model.objects.all():
                self.warm(page.hero_image)
                for photo in page.photos.all():
                    self.warm(photo.picture)

        # People / staff profiles
        for profile in Profile.objects.all():
            self.warm(profile.profile_pic)

        # Publications
        from applications.publications.models import Publication
        for pub in Publication.objects.all():
            self.warm(pub.thumb)

        # Ashram-pattern apps: hero image on the entry, event thumbs, gallery
        # photos, and the app's own list-page HomePage.picture (rendered via
        # {% responsive_img %} in templates/initiative_program/list_about_section.html
        # and each app's own list template). Each app clones the same field names.
        self.warm_ashram_pattern_app('ashram', entry_model_name='Ashram', image_field='image')
        self.warm_ashram_pattern_app('anandakendra', entry_model_name='AnandaKendra', image_field='image')
        self.warm_ashram_pattern_app('charitywork', entry_model_name='Charity', image_field='image')
        self.warm_ashram_pattern_app('ankurayan', entry_model_name='Ankurayan', image_field='logo')
        for app_label in ('sevavrata', 'patriotism', 'prasantaraktadan'):
            self.warm_ashram_pattern_app(app_label, entry_model_name='Ashram', image_field='image')

        # Swabalamban product cards (templates/pillar_page.html: product.image).
        from applications.swabalamban.models import Product
        for product in Product.objects.all():
            self.warm(product.image)

        self.stdout.write(
            self.style.SUCCESS(f'Done. Warmed {self.warmed} image(s), skipped {self.skipped}.')
        )

    def warm(self, field):
        if responsive_image(field):
            self.warmed += 1
        else:
            self.skipped += 1

    def warm_ashram_pattern_app(self, app_label, entry_model_name, image_field):
        """Warm the hero image, event thumbs, gallery photos, and the list
        page's HomePage.picture for one of the Bandhughar-clone apps
        (ashram, anandakendra, charitywork, ankurayan, sevavrata,
        patriotism, prasantaraktadan)."""
        import importlib
        models = importlib.import_module(f'applications.{app_label}.models')
        entry_model = getattr(models, entry_model_name)
        for entry in entry_model.objects.all():
            self.warm(getattr(entry, image_field))

        event_model = getattr(models, 'Event', None)
        if event_model is not None:
            for event in event_model.objects.all():
                self.warm(event.thumb)

        photo_model = getattr(models, 'Photo', None)
        if photo_model is not None:
            for photo in photo_model.objects.all():
                self.warm(photo.picture)

        home_page_model = getattr(models, 'HomePage', None)
        if home_page_model is not None:
            for home in home_page_model.objects.all():
                self.warm(home.picture)
