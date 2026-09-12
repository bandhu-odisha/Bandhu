"""
Fill in blank `Video.duration` values by scraping the YouTube watch page.

This is the only automated writer of `duration`. Run it once after deploying
the home-page load-time fix (which removed the per-request YouTube fetch),
and again whenever a video is added.

Run: python manage.py backfill_video_durations
"""
from django.core.management.base import BaseCommand

from bandhuapp.helpers import enrich_video_durations, youtube_video_id
from bandhuapp.models import Video


class Command(BaseCommand):
    help = 'Fill blank Video.duration values from the YouTube watch page.'

    def handle(self, *args, **options):
        blank_videos = list(Video.objects.filter(duration=''))
        items = []
        for v in blank_videos:
            vid = youtube_video_id(v.script)
            if vid:
                items.append({'video_id': vid, 'duration': None, '_video': v})

        enrich_video_durations(items)

        filled = 0
        for item in items:
            duration = item.get('duration')
            if duration:
                video = item['_video']
                video.duration = duration
                video.save(update_fields=['duration'])
                filled += 1
                self.stdout.write(f'{video.title!r}: {duration}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Filled {filled} of {len(blank_videos)} blank duration(s).'
            )
        )
