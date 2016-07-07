from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from mutopia.forms import AdvSearchForm
from .utilities import load_some_composers, load_some_styles, load_some_instruments

class FormTests(TestCase):

    def setUp(self):
        load_some_instruments()
        load_some_styles()
        load_some_composers()
        
    def test_default_form(self):
        form = AdvSearchForm({})
        self.assertTrue(form.is_valid())
        response = self.client.get(reverse('search'))
        self.assertTemplateUsed(response, 'advsearch.html')
