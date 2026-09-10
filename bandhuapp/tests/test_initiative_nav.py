"""Nav visibility for the newer initiative programs (context processor + API flag)."""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from applications.patriotism import models as patriotism
from applications.prasantaraktadan import models as raktadan
from applications.sevavrata import models as sevavrata
from bandhuapp.initiative_program_year import build_initiative_nav_visibility
from bandhuapp.processors import initiative_nav_visibility
from bandhuapp.tests.support import make_admin


def _entry(models, **extra):
    return models.Ashram.objects.create(
        name='Entry', locality='Cuttack', description='d', address='a',
        image='tests/hero.gif', slug='entry', **extra,
    )


class InitiativeNavVisibilityTests(TestCase):
    def request(self, user=None):
        request = RequestFactory().get('/')
        request.user = user or AnonymousUser()
        return request

    def test_all_hidden_for_public_when_nothing_is_published(self):
        ctx = build_initiative_nav_visibility(self.request())
        self.assertEqual(ctx, {
            'show_initiative_patriotism': False,
            'show_initiative_raktadan': False,
            'show_initiative_sevavrata': False,
        })

    def test_admin_always_sees_every_program(self):
        ctx = build_initiative_nav_visibility(self.request(make_admin()))
        self.assertTrue(all(ctx.values()))

    def test_only_programs_with_public_content_are_shown(self):
        _entry(patriotism, reports='Report')  # has public content -> published
        _entry(raktadan)  # draft
        ctx = build_initiative_nav_visibility(self.request())
        self.assertTrue(ctx['show_initiative_patriotism'])
        self.assertFalse(ctx['show_initiative_raktadan'])
        self.assertFalse(ctx['show_initiative_sevavrata'])

    def test_manually_published_empty_entry_is_reconciled_back_to_draft(self):
        entry = _entry(sevavrata, is_published=True)
        ctx = build_initiative_nav_visibility(self.request())
        self.assertFalse(ctx['show_initiative_sevavrata'])
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_context_processor_exposes_the_same_flags(self):
        _entry(raktadan, reports='Report')
        ctx = initiative_nav_visibility(self.request())
        self.assertEqual(ctx, build_initiative_nav_visibility(self.request()))
        self.assertTrue(ctx['show_initiative_raktadan'])

    def test_flags_reach_rendered_templates(self):
        _entry(raktadan, reports='Report')
        response = self.client.get('/people/')
        self.assertTrue(response.context['show_initiative_raktadan'])
        self.assertFalse(response.context['show_initiative_patriotism'])
