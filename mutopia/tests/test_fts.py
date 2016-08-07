# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db import ProgrammingError
from django.core.urlresolvers import reverse
from mutopia.models import SearchTerm
from .utilities import make_piece, init_fts

class FTSTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.p2 = make_piece(piece_id=2, title='Devil Mountain Rag')
        cls.p3 = make_piece(piece_id=3, title='Suppertime Blues')
        cls.p4 = make_piece(piece_id=4, title='Swingshift Blües') # note diacritical
        init_fts()

    def test_fts_search(self):
        # Test diacritical- and case- insensitive search.
        expected_blues = [str(self.p3), str(self.p4),]
        for term in ['blues', 'Blües', 'BLUES']:
            self.assertQuerysetEqual(SearchTerm.search(term),
                                     expected_blues,
                                     transform=str,
                                     ordered=False)

        # This gets some branch coverage into fts language use.
        p_set = SearchTerm.search('suppertime|mountain')
        self.assertEqual(len(p_set), 2)
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2), str(self.p3),],
                                 transform=str,
                                 ordered=False)

        # The default is an AND of the two search terms
        p_set = SearchTerm.search('devil rag')
        self.assertQuerysetEqual(p_set,
                                 [str(self.p2)],
                                 transform=str )

        # ... so this should return an empty set (but no error)
        p_set = SearchTerm.search('devil swingshift')
        self.assertQuerysetEqual(p_set, [], transform=str )

        # use explicit FTS language to find a blues title without
        # suppertime in its title.
        p_set = SearchTerm.search('blues & !suppertime')
        self.assertQuerysetEqual(p_set, [str(self.p4)], transform=str )

        # On bad input, search raises a programming error. Add others
        # here as you like.
        with self.assertRaises(ProgrammingError):
            p_set = SearchTerm.search('!++&')
