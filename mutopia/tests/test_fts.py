# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db import ProgrammingError
from django.core.urlresolvers import reverse
from .utilities import make_piece, init_fts
from mutopia.views import fts_search

class FTSTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.p2 = make_piece(piece_id=2, title='Devil Mountain Rag')
        cls.p3 = make_piece(piece_id=3, title='Suppertime Blues')
        cls.p4 = make_piece(piece_id=4, title='Swingshift Blües') # note diacritical
        init_fts()

    def test_fts_search(self):
        # Test diacritically insensitive search
        p_set = fts_search('blue')
        self.assertQuerysetEqual(p_set,
                                 [str(self.p3), str(self.p4)],
                                 transform=str,
                                 ordered=False)

        # This gets some branch coverage into fts language use.
        p_set = fts_search('suppertime|mountain')
        self.assertEqual(len(p_set), 2)
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2), str(self.p3)],
                                 transform=str,
                                 ordered=False)


        # The default is an AND of the two search terms
        p_set = fts_search('devil rag')
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2)],
                                 transform=str )
        # ... so this should return an empty set (but no error)
        p_set = fts_search('devil swingshift')
        self.assertQuerysetEqual(p_set, [], transform=str )


        # On bad input, search raises a programming error. Add others
        # here as you like.
        with self.assertRaises(ProgrammingError):
            p_set = fts_search('\(garbage!')
