from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from mutopia.views import handler404
from mutopia.models import Composer, Instrument, Style
from .utilities import load_some_composers, load_some_styles, load_some_instruments
from mudev import urls

class ViewTests(TestCase):
    def setUp(self):
        load_some_composers()
        load_some_styles()
        load_some_instruments()

    def test_404(self):
        self.assertTrue(urls.handler404.endswith('.handler404'))
        factory = RequestFactory()
        request = factory.get('/badurl')
        response = handler404(request)
        self.assertEqual(response.status_code, 404)

    def check_menu(self, name, template):
        response = self.client.get(reverse(name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_all_menus(self):
        p = [('home', 'index.html'),
             ('browse', 'browse.html'),
             ('search', 'advsearch.html'),
             ('legal', 'legal.html'),
             ('contribute', 'contribute.html'),
             ('contact', 'contact.html'),
        ]
        for (name,template) in p:
            self.check_menu(name, template)
