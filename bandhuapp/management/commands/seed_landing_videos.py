"""
Seed landing-page YouTube videos when the table is empty.
Run: python manage.py seed_landing_videos
"""
from django.core.management.base import BaseCommand

from bandhuapp.models import Video

DEFAULT_VIDEOS = [
    {
        'title': 'ANKURAYAN-2025 LOGO UNVELLING',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/icNCtBP4q9w" '
            'title="ANKURAYAN-2025 LOGO UNVELLING" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
    {
        'title': 'ଅନେକ ଆନନ୍ଦର, ଅନେକ ଆକାଂକ୍ଷାର, ଅନେକ ଉଚ୍ଚ୍ଵାସର, ଅନେକ ବିଶ୍ୱାସର.....ସାକ୍ଷୀ ହୋଇ ରହିଛି ମୁଁ ଶ୍ରୀମନ୍ଦିର',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/4rBjRVHNFdE" '
            'title="Bandhu video" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
    {
        'title': 'ଅଙ୍କୁରାୟନ ପିଲାଙ୍କ ଜହ୍ନରାଇଜ 2023',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/9VjKaFIGwBY" '
            'title="Ankurayan childrens sunrise 2023" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
    {
        'title': 'ପିଲାଙ୍କ ଜହ୍ନରାଇଜ - ଅଙ୍କୁରାୟନ 2023',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/BM88oGWv9CA" '
            'title="Children sunrise Ankurayan 2023" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
    {
        'title': 'The voice of Bandhu-2 (ବନ୍ଧୁସ୍ୱର-୨) "ଘାସ"',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/TXfOFMbVoUI" '
            'title="The voice of Bandhu-2" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
    {
        'title': 'The voice of Bandhu - 3 (ବନ୍ଧୁସ୍ୱର -୩)',
        'script': (
            '<iframe width="560" height="315" src="https://www.youtube.com/embed/8_m1pcaa1zY" '
            'title="The voice of Bandhu - 3" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>'
        ),
    },
]


class Command(BaseCommand):
    help = 'Seeds default landing-page YouTube videos when none exist.'

    def handle(self, *args, **options):
        if Video.objects.exists():
            self.stdout.write(self.style.WARNING('Videos already exist; no seed applied.'))
            return

        for item in DEFAULT_VIDEOS:
            Video.objects.create(title=item['title'], script=item['script'])

        self.stdout.write(self.style.SUCCESS(f'Created {len(DEFAULT_VIDEOS)} landing videos.'))
