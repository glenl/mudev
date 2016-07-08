# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db import connection
from .utilities import make_piece
from mutopia.views import fts_search

MATVIEW = """CREATE MATERIALIZED VIEW mu_search_table as
SELECT p.piece_id,
    to_tsvector('english', unaccent(p.title)) ||
    to_tsvector('english', unaccent(c.description)) ||
    to_tsvector('english', unaccent(p.opus)) ||
    to_tsvector('english', p.style_id) ||
    to_tsvector('english', unaccent(p.raw_instrument)) ||
    to_tsvector('english', unaccent(p.lyricist)) ||
    to_tsvector('english', unaccent(p.source)) ||
    to_tsvector('english', unaccent(m.name)) ||
    to_tsvector('english', p.date_composed) ||
    to_tsvector('english', unaccent(p.moreinfo)) ||
    to_tsvector('english', v.version)
        as document
FROM "muPiece" as p
JOIN "muVersion" as v on v.id = p.version_id
JOIN "muComposer" as c on c.composer = p.composer_id
JOIN "muContributor" as m on m.id = p.maintainer_id
"""

DROP_MATVIEW = 'DROP MATERIALIZED VIEW IF EXISTS mu_search_table'
CREATE_INDEX = 'CREATE INDEX idx_fts_search ON mu_search_table USING GIN(document)'

class FTSTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.p2 = make_piece(piece_id=2, title='Devil Mountain Rag')
        cls.p3 = make_piece(piece_id=3, title='Suppertime Blues')
        cls.p4 = make_piece(piece_id=4, title='Swïngshift Blues') # note diacritical

        cursor = connection.cursor()
        cursor.execute(DROP_MATVIEW)
        cursor.execute(MATVIEW)
        cursor.execute(CREATE_INDEX)

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
