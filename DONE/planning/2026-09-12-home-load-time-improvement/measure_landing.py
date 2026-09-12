"""Measure the cost of the YouTube scrape inside _build_landing_data.

Run from the repo root with the venv that actually has Django installed:

    ./.venv/bin/python DONE/planning/2026-09-12-home-load-time-improvement/measure_landing.py

Read-only: everything runs inside a transaction that is rolled back.
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandhu.settings')

import django

django.setup()

from django.contrib.auth.models import AnonymousUser
from django.db import connection, transaction
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from bandhuapp import views
from bandhuapp.models import Video


def build_once(label):
    request = RequestFactory().get('/')
    request.user = AnonymousUser()
    with CaptureQueriesContext(connection) as ctx:
        start = time.perf_counter()
        views._build_landing_data(request)
        elapsed = (time.perf_counter() - start) * 1000
    print('{:<26} {:>10.1f} ms  {:>3} queries'.format(label, elapsed, len(ctx)))


def main():
    total = Video.objects.count()
    blank = Video.objects.filter(duration='').count()
    print('Video rows: {}   blank duration: {}'.format(total, blank))
    print('')

    # Step 1 removed the per-request YouTube fetch entirely (no more
    # `views.enrich_video_durations` to patch/compare against) -- three runs,
    # all "fetch-free" by construction, replace the old stubbed/live/stubbed rows.
    build_once('1. warm-up')
    build_once('2. steady state')
    build_once('3. steady state (control)')


if __name__ == '__main__':
    try:
        with transaction.atomic():
            main()
            raise RuntimeError('__rollback__')
    except RuntimeError as exc:
        if str(exc) != '__rollback__':
            raise
        print('')
        print('(transaction rolled back - database unchanged)')
