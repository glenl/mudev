# -*- coding: utf-8 -*-
from django.test import TestCase
from mutopia.utils import id_from_footer

class UtilityTests(TestCase):

    def test_id_from_footer(self):
        footer = 'Mutopia-12/10/200-123'
        (pdate,id) = id_from_footer(footer)
        self.assertEqual(id, '123')
