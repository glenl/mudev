import re
from django.test import TestCase
from django.utils.text import slugify
from django.utils import timezone
from mutopia.models import Composer, Contributor, Style, LPVersion, Piece
from mutopia.models import UpdateMarker, License, AssetMap, RawInstrumentMap
from mutopia.models import Instrument
from mutopia.models import Collection
from .utilities import make_piece

class ComposerTests(TestCase):
    def test_composer(self):
        homer,_ = Composer.objects.get_or_create(composer='SimpsonH',
                                               description='Homer Simpson(1999--)')
        self.assertTrue(isinstance(homer, Composer))
        self.assertEqual(str(homer), homer.composer)
        self.assertFalse(re.search('[\(\)0-9]', homer.rawstr()))

    def test_composer_byline(self):
        trad = Composer.objects.create(composer='Traditional')
        self.assertTrue(isinstance(trad, Composer))
        self.assertFalse(re.search('by', trad.byline()))
        homer,_ = Composer.objects.get_or_create(composer='SimpsonH',
                                                 description='Homer Simpson(1999--)')
        self.assertTrue(re.search('by', homer.byline()))

class ContributorTests(TestCase):
    def test_contributor(self):
        # create a contributor
        c,_ = Contributor.objects.get_or_create(name='John Smith',
                                                email='JSmith@example.com',
                                                url='johnsmith.com')
        self.assertTrue(isinstance(c, Contributor))
        self.assertFalse(re.search('@', c.reformat_email()))
        self.assertEqual(c.__str__(), c.name)
        # find an existing contributor
        c2,_ = Contributor.objects.get_or_create(name='John Smith')
        self.assertEqual(c.email, c2.email)

    def test_missing_field(self):
        # create a contributor with no email field
        no_email,_ = Contributor.objects.get_or_create(name='Jason Smith', url='jasonsmith.com')
        self.assertTrue(isinstance(no_email, Contributor))
        self.assertFalse(re.search('@', no_email.reformat_email()))
        self.assertEqual(len(no_email.email), len(no_email.reformat_email()))


class StyleTests(TestCase):

    def test_style(self):
        sluggable = Style.find_or_create('old age')
        self.assertTrue(isinstance(sluggable, Style))
        self.assertEqual(str(sluggable), sluggable.style)
        self.assertNotEqual(str(sluggable), sluggable.slug)


class LPVersionTests(TestCase):

    def test_version(self):
        v1 = LPVersion.find_or_create('1.2.3')
        self.assertTrue(isinstance(v1, LPVersion))
        self.assertTrue(str(v1))
        self.assertEqual(v1.major, '1')
        self.assertEqual(v1.minor, '2')
        self.assertEqual(v1.edit, '3')
        self.assertEqual(v1.__str__(), v1.version)
        v2 = LPVersion.find_or_create('1.2.3')
        self.assertEqual(str(v1), str(v2))

        # for a branch test
        v3 = LPVersion.find_or_create('12.2')
        self.assertTrue(isinstance(v3, LPVersion))

        with self.assertRaisesMessage(IndexError, 'list index out of range'):
            v4 = LPVersion.find_or_create('10')

class PieceTests(TestCase):
    def test_piece(self):
        p = make_piece()
        self.assertTrue(isinstance(p, Piece))
        self.assertTrue('-' in str(p))

class UpdateMarkerTest(TestCase):
    def test_marker(self):
        m = UpdateMarker.objects.create(updated_on=timezone.now())
        self.assertTrue(isinstance(m, UpdateMarker))
        self.assertTrue(str(m))

class LicenseTests(TestCase):
    def test_license(self):
        cc = License.objects.create(name='Public', url='http://public-domain/')
        self.assertTrue(isinstance(cc, License))
        self.assertTrue(str(cc))

class AssetMapTests(TestCase):
    def check_accessors(self, asset):
        self.assertTrue(asset.get_midi())
        self.assertTrue(asset.get_ly())
        self.assertTrue(asset.get_ps_a4())
        self.assertTrue(asset.get_ps_let())
        self.assertTrue(asset.get_pdf_a4())
        self.assertTrue(asset.get_pdf_let())

    def test_asset_map(self):
        p = make_piece()
        asset = AssetMap.objects.create(folder='/'.join([str(p.composer), 'swings',]),
                                        name='swings-piece', has_lys=False)
        # should be able to create an asset with a null piece
        self.assertTrue(isinstance(asset, AssetMap))
        self.assertTrue(str(asset))
        p.piece = p

        # get us some coverage on the accessors.
        self.assertEqual(asset.get_composer(), str(p.composer))
        self.check_accessors(asset)
        asset.has_lys = True
        self.check_accessors(asset)

class InstrumentTests(TestCase):
    def test_instrument(self):
        k,_ = Instrument.objects.get_or_create(instrument='kazoo', in_mutopia=False)
        self.assertTrue(isinstance(k, Instrument))
        k.save()
        k2,_ = Instrument.objects.get_or_create(instrument='kazoo')
        self.assertEqual(k, k2)

class RawInstrumentMapTests(TestCase):
    def test_instrument_map(self):
        bagpipe,_ = Instrument.objects.get_or_create(instrument='bagpipe')
        self.assertTrue(str(bagpipe))
        r1 = RawInstrumentMap.objects.create(raw_instrument='Windbag',
                                             instrument=bagpipe)
        self.assertTrue(str(r1))


class CollectionTest(TestCase):
    def test_collections(self):
        ctitle = 'Test Collection'
        c,_ = Collection.objects.get_or_create(tag='testc',title=ctitle)
        self.assertTrue(isinstance(c, Collection))
        self.assertTrue(str(c))
        self.assertTrue(c.user_infofile().endswith('info.dat'))

        p = make_piece()
        # not yet a part of any collection
        colset = p.collection_set.all()
        self.assertQuerysetEqual(colset, [])

        # add the piece
        c.pieces.add(p)
        # get the set of collections from the piece
        colset = p.collection_set.all()
        self.assertQuerysetEqual(colset, [str(c)], transform=str)
