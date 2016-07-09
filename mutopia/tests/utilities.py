from datetime import date
from django.db import connection
from mutopia.models import Composer, Instrument, Style, Piece
from mutopia.models import License, Contributor, LPVersion, AssetMap

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
DROP_INDEX = 'DROP INDEX IF EXISTS idx_fts_search'
CREATE_INDEX = 'CREATE INDEX idx_fts_search ON mu_search_table USING GIN(document)'

def init_fts():
    cursor = connection.cursor()
    cursor.execute(DROP_MATVIEW)
    cursor.execute(MATVIEW)
    cursor.execute(DROP_INDEX)
    cursor.execute(CREATE_INDEX)
    

def load_some_styles():
    for s in ['Ska', 'Reggae', 'Swing',]:
        Style.find_or_create(s)


def load_some_composers():
    Composer.objects.get_or_create(composer='MouseM', description='Mickey Mouse (1928--)')
    Composer.objects.get_or_create(composer='OylO', description='Olive Oyl (1928--)')


def load_some_instruments():
    Instrument.objects.get_or_create(instrument='Uke', in_mutopia=True)
    Instrument.objects.get_or_create(instrument='Banjo', in_mutopia=True)


def make_piece(piece_id=1, title='Flimmin on the Jimjam'):
    try:
        p = Piece.objects.get(pk=piece_id)
        return p
    except Piece.DoesNotExist:
        pass

    c,_ = Composer.objects.get_or_create(composer='JayJ',
                                         description='Joe Jay (1888--1944')
    s = Style.find_or_create('Bop')
    v = LPVersion.find_or_create('2.19.35')
    m,_ = Contributor.objects.get_or_create(name='John Smith', 
                                            email='JSmith@example.com',
                                            url='johnsmith.com')
    cc,_ = License.objects.get_or_create(name='Public', url='http://public-domain/')
    p = Piece.objects.create(piece_id=piece_id,
                             title=title,
                             composer=c,
                             style=s,
                             raw_instrument='Piano',
                             license=cc,
                             maintainer=m,
                             version=v,
                             date_composed='recently',
                             date_published=date.today(),
                             source='original manuscript')
    p.save()
    piano, _ = Instrument.objects.get_or_create(instrument='Piano', in_mutopia=True)
    p.instruments.add(piano)
    p.save()
    return p
