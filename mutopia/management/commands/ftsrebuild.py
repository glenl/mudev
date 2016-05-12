from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from mutopia.models import Piece
import re
import pprint
"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(kws)
"""

def get_keywords(p):
    kws = [p.title, str(p.piece_id),
           p.opus, p.composer.rawstr(),
           p.raw_instrument, p.style.style,
           p.version.version, p.lyricist,
           p.source, p.date_composed, p.moreinfo,]
    kstr = ', '.join(kws).rstrip(', ').replace(', ,', ',')
    return kstr


class Command(BaseCommand):
    help = 'load the fts tables for SQLite'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS muPieceKeys")
        self.stdout.write('populating muPieceKeys ...')
        cursor.execute("""CREATE VIRTUAL TABLE muPieceKeys
               USING fts4(piece_id, keywords, tokenize=unicode61)""")
        cursor.execute("BEGIN");
        for p in Piece.objects.all():
            cursor.execute("INSERT INTO muPieceKeys VALUES(%s, %s)",
                           [p.piece_id, get_keywords(p)])
        cursor.execute("COMMIT");
