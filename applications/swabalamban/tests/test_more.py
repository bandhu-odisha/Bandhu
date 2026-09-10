"""Swabalamban model helpers, image_utils and admin (create_product lives in test_products.py)."""

from unittest import mock

from django.test import TestCase

from applications.swabalamban.image_utils import image_field_url, static_image_url
from applications.swabalamban.models import Product
from bandhuapp.tests.support import TempMediaMixin, image_upload, make_admin


class ProductModelTests(TempMediaMixin, TestCase):
    def test_capitalize_label(self):
        self.assertEqual(Product.capitalize_label('premium RICE'), 'Premium Rice')
        self.assertEqual(Product.capitalize_label('  '), '')
        self.assertEqual(Product.capitalize_label(None), '')

    def test_save_title_cases_label_and_helpers_split_lines(self):
        product = Product.objects.create(
            name='Dal', label='red DAL', image='t/d.gif', intro_text='x',
            nutritional_highlights='  one \n\n two\n', quality_promise='',
        )
        self.assertEqual(product.label, 'Red Dal')
        self.assertEqual(str(product), 'Dal')
        self.assertEqual(product.modal_id, f'productModal{product.pk}')
        self.assertEqual(product.highlight_list, ['one', 'two'])
        self.assertEqual(product.quality_promise_list, [])
        product.quality_promise = 'a\n b '
        self.assertEqual(product.quality_promise_list, ['a', 'b'])

    def test_default_ordering(self):
        b = Product.objects.create(name='B', label='b', image='t/b.gif', intro_text='x', sort_order=1)
        a = Product.objects.create(name='A', label='a', image='t/a.gif', intro_text='x', sort_order=1)
        z = Product.objects.create(name='Z', label='z', image='t/z.gif', intro_text='x', sort_order=0)
        self.assertEqual(list(Product.objects.all()), [z, a, b])


class ImageUtilsTests(TempMediaMixin, TestCase):
    def test_image_field_url_only_for_files_present_in_storage(self):
        missing = Product.objects.create(name='M', label='m', image='t/missing.gif', intro_text='x')
        self.assertIsNone(image_field_url(missing.image))

        present = Product.objects.create(name='P', label='p', image=image_upload('p.gif'), intro_text='x')
        self.assertEqual(image_field_url(present.image), present.image.url)

        blank = Product(name='N', label='n', intro_text='x')
        self.assertIsNone(image_field_url(blank.image))
        self.assertIsNone(image_field_url(None))

    def test_image_field_url_swallows_storage_errors(self):
        product = Product.objects.create(name='E', label='e', image='t/e.gif', intro_text='x')
        with mock.patch.object(product.image.storage, 'exists', side_effect=OSError('boom')):
            self.assertIsNone(image_field_url(product.image))

    def test_static_image_url(self):
        self.assertEqual(static_image_url('img/x.png'), '/static/img/x.png')


class ProductAdminTests(TempMediaMixin, TestCase):
    def test_changelist_with_editable_columns_and_add_form(self):
        product = Product.objects.create(name='Dal', label='d', image='t/d.gif', intro_text='x', sort_order=3)
        self.client.force_login(make_admin())
        response = self.client.get('/admin/swabalamban/product/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dal')
        self.assertEqual(self.client.get('/admin/swabalamban/product/add/').status_code, 200)
        self.assertEqual(self.client.get(f'/admin/swabalamban/product/{product.pk}/change/').status_code, 200)
