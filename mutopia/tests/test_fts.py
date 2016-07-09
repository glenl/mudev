# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from .utilities import make_piece, init_fts
from mutopia.views import fts_search

class FTSTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.p2 = make_piece(piece_id=2, title='Devil Mountain Rag')
        cls.p3 = make_piece(piece_id=3, title='Suppertime Blues')
        cls.p4 = make_piece(piece_id=4, title='Swïngshift Blues') # note diacritical
        init_fts()

    def test_fts_search(self):
        p_set = fts_search('blue')
        self.assertQuerysetEqual(p_set,
                                 [str(self.p3), str(self.p4)],
                                 transform=str,
                                 ordered=False)

        # this gets some branch coverage into fts language use.
        p_set = fts_search('suppertime|mountain')
        self.assertEqual(len(p_set), 2)
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2), str(self.p3)],
                                 transform=str,
                                 ordered=False)


        p_set = fts_search('devil rag')
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2)],
                                 transform=str )
