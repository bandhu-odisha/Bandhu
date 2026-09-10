"""Guards against the whole `applications/` half of the suite silently disappearing.

`applications/` must stay a REGULAR package (i.e. keep its `__init__.py`). If that file
is deleted, Python treats `applications` as a namespace package and two things happen,
neither of which looks like a failure:

1. `manage.py test` discovers only the `accounts` and `bandhuapp` tests -- 285 instead
   of 596 -- and still prints OK. Every initiative-program regression test is skipped.
2. `manage.py test applications.<app>` dies inside unittest's loader with
   `TypeError: expected str, bytes or os.PathLike object, not NoneType`, because a
   namespace package has `__file__ = None`.

These tests live in `bandhuapp` (not `applications`) on purpose: they must still be
discovered in exactly the situation they are designed to detect.
"""

import importlib
import unittest

from django.apps import apps
from django.conf import settings


class ApplicationsIsARegularPackageTests(unittest.TestCase):
    def test_applications_package_has_a_file_so_discovery_can_walk_it(self):
        package = importlib.import_module('applications')
        self.assertIsNotNone(
            package.__file__,
            "applications/__init__.py is missing, so `applications` is a namespace "
            "package. Test discovery will silently skip every applications/* test "
            "while still reporting success. Restore the empty __init__.py.",
        )

    def test_every_installed_application_app_is_importable_and_has_tests(self):
        """Each `applications.*` entry in INSTALLED_APPS must expose a tests package."""
        labels = [
            entry for entry in settings.INSTALLED_APPS
            if entry.startswith('applications.')
        ]
        self.assertGreaterEqual(len(labels), 11, 'INSTALLED_APPS lost applications entries')

        missing = []
        for dotted in labels:
            try:
                importlib.import_module(dotted + '.tests')
            except ImportError:
                missing.append(dotted)
        self.assertEqual(missing, [], 'these apps have no importable tests package')

    def test_app_registry_resolves_every_applications_entry(self):
        """Catches an `apps.py` AppConfig.name drifting away from its dotted path."""
        for dotted in settings.INSTALLED_APPS:
            if not dotted.startswith('applications.'):
                continue
            label = dotted.rsplit('.', 1)[1]
            self.assertTrue(
                apps.is_installed(dotted) or apps.get_app_config(label) is not None,
                '%s is not resolvable in the app registry' % dotted,
            )
