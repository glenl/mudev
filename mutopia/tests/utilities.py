from datetime import date
from mutopia.models import Composer, Instrument, Style, Piece
from mutopia.models import License, Contributor, LPVersion, AssetMap
from mutopia.models import SearchTerm

def init_fts():
    SearchTerm.rebuild_view()
    SearchTerm.refresh_view()


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
