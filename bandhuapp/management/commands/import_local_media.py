"""
Copy bundled img/ assets into MEDIA_ROOT for local development.
Run: python manage.py import_local_media
"""
import hashlib
import os
import re
import shutil

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField, ImageField

from bandhuapp.models import AboutUs, Gallery, Photo

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ABOUT_SLIDE_PREFIX = 'about-slide'
PLACEHOLDER_GALLERY_BASENAMES = {
    'pimg1.jpg', 'pimg2.jpg', 'pimg3.jpg', 'pimg4.jpg', 'pimg5.jpg',
    'pimg6.jpg', 'pimg7.jpg', 'pimg8.jpg', 'pimg9.jpg',
    'gimg-1.png', 'gimg-2.png', 'gimg-3.png',
    'clients-bg.jpg', 'clients-bg1.jpg', 'vol3-may19.jpg',
}
ABOUT_COPY = {
    'tagline': 'Bandhu is an idea that celebrates goodness, that is in you, me and all others.',
    'desc': (
        'We are a group of people, good but not necessarily great, with a spontaneous '
        'flow of boundless friendship. The concern is about the inconsistencies within '
        'and without. Bandhu does small things with the highest possible sincerity.'
    ),
}
GALLERY_TAGLINE = (
    'Take a look at our gallery to get a glimpse of what we do and what it feels like '
    'working for a social cause.'
).replace('\n', ' ').strip()
DUPLICATE_SUFFIX_RE = re.compile(r'_[A-Za-z0-9]{6,7}$')


class Command(BaseCommand):
    help = 'Copies missing local media files from the project img/ folder into MEDIA_ROOT.'

    def _canonical_gallery_stem(self, filename):
        stem, _ext = os.path.splitext(filename)
        return DUPLICATE_SUFFIX_RE.sub('', stem).lower()

    def _should_skip_gallery_file(self, filename):
        lowered = filename.lower()
        if ABOUT_SLIDE_PREFIX in lowered:
            return True
        if lowered in PLACEHOLDER_GALLERY_BASENAMES:
            return True
        if os.path.splitext(lowered)[1] not in IMAGE_EXTENSIONS:
            return True
        if any(token in lowered for token in ('logo', 'publication', 'publicationsd', 'swamblamban')):
            return True
        return False

    def _infer_gallery_tags(self, filename):
        lowered = filename.lower()
        if 'ankurayan' in lowered:
            return 'ankurayan'
        if any(token in lowered for token in ('anandakendra', 'ananda', 'kendra', 'kahana', 'paika')):
            return 'anandakendra'
        if any(token in lowered for token in ('bandhughar', 'bandhughara')):
            return 'bandhughar'
        if any(token in lowered for token in ('sanskar', 'sansara', 'swami', 'meeting', 'council', 'gc_')):
            return 'activities'
        return 'other'

    def _import_site_content(self):
        about = AboutUs.objects.first()
        if not about:
            about = AboutUs.objects.create(**ABOUT_COPY)
        else:
            for field, value in ABOUT_COPY.items():
                setattr(about, field, value)
            about.save()

        gallery = Gallery.objects.first()
        if not gallery:
            Gallery.objects.create(tagline=GALLERY_TAGLINE)
        else:
            gallery.tagline = GALLERY_TAGLINE
            gallery.save()

    def _sync_gallery_photos(self, media_root):
        gallery_dir = os.path.join(media_root, 'bandhuapp', 'gallery')
        if not os.path.isdir(gallery_dir):
            return 0

        Photo.objects.filter(picture__startswith='main_page/initiatives/').delete()

        grouped = {}
        for filename in sorted(os.listdir(gallery_dir)):
            src = os.path.join(gallery_dir, filename)
            if not os.path.isfile(src) or self._should_skip_gallery_file(filename):
                continue
            digest = hashlib.md5(open(src, 'rb').read()).hexdigest()
            grouped.setdefault(digest, []).append(filename)

        canonical_paths = set()
        for filenames in grouped.values():
            canonical_name = sorted(
                filenames,
                key=lambda name: (len(name), self._canonical_gallery_stem(name), name.lower()),
            )[0]
            canonical_paths.add(f'bandhuapp/gallery/{canonical_name}')

        Photo.objects.filter(picture__startswith='bandhuapp/gallery/').exclude(
            picture__in=canonical_paths,
        ).delete()

        synced = 0
        for relative_path in sorted(canonical_paths):
            filename = os.path.basename(relative_path)
            photo = Photo.objects.filter(picture=relative_path).first()
            if not photo:
                photo = Photo(picture=relative_path)
            photo.tags = self._infer_gallery_tags(filename)
            photo.approved = True
            if not photo.caption:
                photo.caption = self._canonical_gallery_stem(filename).replace('_', ' ').replace('-', ' ').strip()
            photo.save()
            synced += 1
        return synced

    def handle(self, *args, **options):
        img_root = os.path.join(settings.BASE_DIR, 'img')
        media_root = settings.MEDIA_ROOT
        if not os.path.isdir(img_root):
            self.stderr.write(self.style.ERROR(f'Missing img directory: {img_root}'))
            return

        img_index = {}
        for name in os.listdir(img_root):
            src = os.path.join(img_root, name)
            if os.path.isfile(src):
                img_index[name.lower()] = src

        aliases = {
            'ankurayan.jpg': 'pimg1.jpg',
            'publicationsd.jpg': 'publicationSD.jpg',
            'publication.jpg': 'publication.jpg',
            'otheractivity_poster.jpg': 'clients-bg.jpg',
            'collage.jpg': 'clients-bg1.jpg',
            'griga.jpg': 'gimg-1.png',
            'photo.jpg': 'dummy.jpg',
        }
        explicit_sources = {
            'bandhuapp/banner/our_mission.jpg': 'our_mission.jpg',
            'bandhuapp/banner/our_mission2.jpg': 'our_mission2.jpg',
            'bandhuapp/banner/event-section-bg.jpg': 'event-section-bg.jpg',
            'bandhuapp/sanskar/our_mission.jpg': 'our_mission.jpg',
            'bandhuapp/swaraj/our_mission1.jpg': 'our_mission1.jpg',
            'bandhuapp/swabalamban/pimg2.jpg': 'pimg2.jpg',
            'bandhuapp/gallery/about-slide-1-gardenia.png': 'about-slide-1-gardenia.png',
            'bandhuapp/gallery/about-slide-2-hibiscus.png': 'about-slide-2-hibiscus.png',
            'bandhuapp/gallery/about-slide-3-campus.png': 'about-slide-3-campus.png',
            'bandhuapp/gallery/about-slide-4-ixora.png': 'about-slide-4-ixora.png',
            'bandhuapp/gallery/about-slide-blossoms.png': 'about-slide-blossoms.png',
            'profile_photos/man.png': 'man.png',
            'profile_photos/woman.png': 'woman.png',
        }

        needed = set()
        for model in apps.get_models():
            file_fields = [
                field for field in model._meta.get_fields()
                if isinstance(field, (FileField, ImageField))
            ]
            if not file_fields:
                continue
            for row in model.objects.all().iterator():
                for field in file_fields:
                    file_field = getattr(row, field.name, None)
                    if file_field and getattr(file_field, 'name', None):
                        needed.add(file_field.name.replace('\\', '/'))

        for relative_path in explicit_sources:
            needed.add(relative_path)

        copied = 0
        missing = 0
        for relative_path in sorted(needed):
            dest = os.path.join(media_root, relative_path)
            if os.path.isfile(dest):
                continue

            basename = os.path.basename(relative_path)
            source_name = explicit_sources.get(relative_path)
            src = img_index.get(source_name.lower()) if source_name else None
            if not src:
                src = img_index.get(basename.lower())
            if not src:
                alias = aliases.get(basename.lower())
                if alias:
                    src = img_index.get(alias.lower())
            if not src:
                missing += 1
                self.stdout.write(self.style.WARNING(f'No local source for {relative_path}'))
                continue

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            copied += 1
            self.stdout.write(f'Copied {os.path.basename(src)} -> {relative_path}')

        synced = self._sync_gallery_photos(media_root)
        self._import_site_content()
        from django.core.management import call_command
        call_command('seed_landing_notices')
        call_command('seed_people')
        call_command('seed_ashram_content')
        call_command('seed_charitywork_content')
        call_command('seed_publications_content')
        call_command('seed_ankurayan_content')
        call_command('seed_anandakendra_content')
        self.stdout.write(self.style.SUCCESS(
            f'Copied {copied} file(s); {missing} unresolved path(s); synced {synced} gallery photo(s).'
        ))
