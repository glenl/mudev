from datetime import date
from mutopia.models import Composer, Instrument, Style, Piece
from mutopia.models import License, Contributor, LPVersion
from django.utils.text import slugify

def create_style(s):
    return Style.objects.create(style=s, slug=slugify(s), in_mutopia=True)

def load_some_styles():
    create_style('Ska').save()
    create_style('Reggae').save()

def load_some_composers():
    Composer.objects.create(composer='MouseM', description='Mickey Mouse (1928--)').save()
    Composer.objects.create(composer='OylO', description='Olive Oyl (1928--)').save()

def load_some_instruments():
    Instrument.objects.create(instrument='Uke', in_mutopia=True).save()
    Instrument.objects.create(instrument='Banjo', in_mutopia=True).save()

def make_piece():
    c = Composer.objects.create(composer='JayJ', description='Joe Jay (1888--1944')
    c.save()
    s = create_style('Swing')
    s.save()
    v = LPVersion.find_or_create('2.19.35')
    m = Contributor.find_or_create('John Smith', 'JSmith@example.com', 'johnsmith.com')
    cc = License.objects.create(name='Public', url='http://public-domain/')
    p = Piece.objects.create(piece_id=1,
                             title='Flimmin on the Jimjam',
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
    instr = Instrument.objects.create(instrument='Piano', in_mutopia=True)
    instr.save()
    p.instruments.add(instr)
    p.save()
    return p
