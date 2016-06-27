from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from mutopia.models import Piece
import re
import pprint


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

class Command(BaseCommand):
    help = 'build and load the fts tables for PostGreSQL'

    def add_arguments(self, parser):
        parser.add_argument('--refresh',
                            action='store_true',
                            dest='refresh',
                            default=False,
                            help='refresh materialized view only')

    def handle(self, *args, **options):
        cursor = connection.cursor()
        if options['refresh']:
            cursor.execute('REFRESH MATERIALIZED VIEW mu_search_table')
        else:
            self.stdout.write('creating new search table ...')
            cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mu_search_table')
            cursor.execute(MATVIEW)
            self.stdout.write('populating mu_search_index ...')
            cursor.execute('CREATE INDEX idx_fts_search ON mu_search_table USING GIN(document)')
