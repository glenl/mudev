# -*- coding: utf-8 -*-
"""
These are search-related elements for the |django| ORM, which have
been moved to a separate model because the FTS implementation with
requires a *hybrid* implementation that is different than the other
models. The functionality was moved here to make it easier to support
test routines for our FTS implementation.

There is no FTS support in |django| but it can be made to work with a
model that shadows a |postgres| materialized view built to contain
search terms in a specially constructed document.

.. moduleauthor:: Glen Larsen, glenl.glx at gmail.com

"""
import re
import string
from django.db import connection
from django.db import models
from .models import Piece

MV_NAME = 'mu_search_view'
MV_INDEX_NAME = 'mu_search_index'
MV_DROP = 'DROP MATERIALIZED VIEW IF EXISTS {0}'
MV_CREATE = """
CREATE MATERIALIZED VIEW {0}
(id, piece_id, document)
AS SELECT
    p.piece_id,
    p.piece_id,
    (to_tsvector('pg_catalog.simple',
        concat_ws(' ', unaccent(p.title),
            unaccent(c.description),
            unaccent(p.opus),
            p.style_id,
            unaccent(p.raw_instrument),
            unaccent(p.lyricist),
            unaccent(p.source),
            unaccent(m.name),
            p.date_composed,
            unaccent(p.moreinfo),
            v.version)
        )) AS document
    FROM "muPiece" as p
    JOIN "muVersion" as v on v.id = p.version_id
    JOIN "muComposer" as c on c.composer = p.composer_id
    JOIN "muContributor" as m on m.id = p.maintainer_id
"""

MV_INDEX_DROP = 'DROP INDEX IF EXISTS {0}'
MV_INDEX_CREATE = 'CREATE INDEX {0} ON {1} USING GIN(document)'
MV_REFRESH = 'REFRESH MATERIALIZED VIEW {0}'

# FTS is not supported directly in Django so we are going to execute a
# manual query. This is a format string that is designed to be filled
# in by a keyword sanitized to form the query.
_PG_FTSQ = ' '.join([ "SELECT piece_id FROM",
                      MV_NAME,
                      "WHERE document @@ to_tsquery('pg_catalog.simple', unaccent(%s))"])

class SearchTerm(models.Model):
    """A model to shadow a Postgres materialized view containing a
    document containing search terms associated with the given
    :class:`mutopia.models.Piece`.

    The shadowed table should be refreshed after any updates.

    """

    #:The target piece for this search document.
    piece_id = models.ForeignKey(Piece)

    #:The search document for FTS
    document = models.TextField()

    class Meta:
        db_table = MV_NAME
        managed = False

    @classmethod
    def rebuild_view(cls):
        """Drop and re-create the materialized view and its index."""

        cursor = connection.cursor()
        cursor.execute(MV_DROP.format(MV_NAME))
        cursor.execute(MV_CREATE.format(MV_NAME))
        cursor.execute(MV_INDEX_DROP.format(MV_INDEX_NAME))
        cursor.execute(MV_INDEX_CREATE.format(MV_INDEX_NAME, MV_NAME))

    @classmethod
    def refresh_view(cls):
        """Refresh the associated view.

        After updates and inserts, the materialized view needs to be
        refreshed. We could do this with a trigger but for now it is
        simple enough to do it from this class method after processing
        submissions.

        """

        cursor = connection.cursor()
        cursor.execute(MV_REFRESH.format(MV_NAME))

    @classmethod
    def _sanitize(cls, term):
        """Sanitize input to the search routine.

        :param str term: Input string to clean.
        :return: A sanitized string, ready for FTS.

        """
        # Replace all puncuation with spaces.
        allowed_punctuation = set(['&', '|', '"', "'", '!'])
        all_punctuation = set(string.punctuation)
        punctuation = ''.join(all_punctuation - allowed_punctuation)
        term = re.sub(r'[{}]+'.format(re.escape(punctuation)), ' ', term)

        # Substitute all double quotes to single quotes.
        term = term.replace('"', "'")
        term = re.sub(r"'+", "'", term)

        # if no special characters, and search terms together.
        if not re.search('[&|!]', term):
            term = re.sub(r'\s+', ' & ', term)

        return term


    @classmethod
    def search(cls, keywords):
        """Given keyword string, search using FTS. Because FTS is not a
        supported feature of django, it is faked here by using a
        manual query that returns :class:`mutopia.models.Piece` keys.

        :param str keywords: Input from the user
        :return: Zero or more Pieces.
        :rtype: A Piece query set.

        """

        terms = cls._sanitize(keywords)
        cursor = connection.cursor()
        results = []
        try:
            cursor.execute(_PG_FTSQ, [terms,])
            results = [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()

        # The results from manual queries do not return true QuerySets
        # so these are translated for the caller with a filter.
        return Piece.objects.filter(pk__in=results)
