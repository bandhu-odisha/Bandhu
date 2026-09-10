from django.test import TestCase

from applications.swabalamban.models import Product
from bandhuapp.tests.support import TempMediaMixin, image_upload, make_admin, make_user

CREATE = '/swabalamban/create/product/'


def product_form(**overrides):
    data = {
        'name': 'Red Dal', 'label': 'Dal', 'intro_lead': 'lead', 'intro_text': 'body',
        'nutritional_highlights': '', 'quality_promise': '', 'image': image_upload(),
    }
    data.update(overrides)
    return data


class SwabalambanProductTests(TempMediaMixin, TestCase):
    def test_public_page_lists_only_published_products(self):
        shown = Product.objects.create(name='A', label='a', image='t/a.gif', intro_text='x', is_published=True)
        Product.objects.create(name='B', label='b', image='t/b.gif', intro_text='x', is_published=False)
        response = self.client.get('/swabalamban/')
        self.assertEqual(list(response.context['products']), [shown])

    def test_create_requires_admin(self):
        self.assertEqual(self.client.post(CREATE, product_form()).status_code, 302)
        self.client.force_login(make_user())
        self.assertRedirects(self.client.post(CREATE, product_form()), '/swabalamban/', fetch_redirect_response=False)
        self.assertEqual(Product.objects.count(), 0)

    def test_admin_creates_published_product_with_next_sort_order(self):
        Product.objects.create(name='Existing', label='e', image='t/e.gif', intro_text='x', sort_order=4)
        self.client.force_login(make_admin())
        self.assertRedirects(self.client.get(CREATE), '/swabalamban/', fetch_redirect_response=False)
        response = self.client.post(CREATE, product_form())
        self.assertRedirects(response, '/swabalamban/#our-products', fetch_redirect_response=False)
        product = Product.objects.get(name='Red Dal')
        self.assertTrue(product.is_published)
        self.assertEqual(product.sort_order, 5)

    def test_missing_fields_and_duplicate_names_are_rejected(self):
        self.client.force_login(make_admin())
        self.client.post(CREATE, product_form(intro_text=''))
        self.assertEqual(Product.objects.count(), 0)
        self.client.post(CREATE, product_form())
        self.client.post(CREATE, product_form(name='red dal'))
        self.assertEqual(Product.objects.count(), 1)
