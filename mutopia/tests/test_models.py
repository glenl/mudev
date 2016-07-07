import re
from django.test import TestCase
from django.utils.text import slugify
from django.utils import timezone
from mutopia.models import Composer, Contributor, Style, LPVersion, Piece
from mutopia.models import UpdateMarker, License, AssetMap, RawInstrumentMap
from mutopia.models import Instrument
from .utilities import make_piece

class ComposerTests(TestCase):
    def test_composer(self):
        homer = Composer.objects.create(composer='SimpsonH', description='Homer Simpson(1999--)')
        self.assertTrue(isinstance(homer, Composer))
        self.assertEqual(homer.__str__(), homer.composer)
        self.assertFalse(re.search('[\(\)0-9]', homer.rawstr()))


class ContributorTests(TestCase):
    def test_contributor(self):
        # create a contributor
        c = Contributor.find_or_create('John Smith', 'JSmith@example.com', 'johnsmith.com')
        self.assertTrue(isinstance(c, Contributor))
        self.assertFalse(re.search('@', c.reformat_email()))
        self.assertEqual(c.__str__(), c.name)
        # find an existing contributor
        c2 = Contributor.find_or_create('John Smith')
        self.assertEqual(c.email, c2.email)

    def test_missing_field(self):
        # create a contributor with no email field
        no_email = Contributor.find_or_create('Jason Smith', url='jasonsmith.com')
        self.assertFalse(re.search('@', no_email.reformat_email()))
        self.assertEqual(len(no_email.email), len(no_email.reformat_email()))


class StyleTests(TestCase):
    def create_style(self, s):
        return Style.objects.create(style=s, slug=slugify(s), in_mutopia=False)

    def test_style(self):
        sluggable = self.create_style('old age')
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
        k = Instrument.objects.create(instrument='kazoo', in_mutopia=False)
        self.assertTrue(isinstance(k, Instrument))
        k.save()
        k2 = Instrument.find_or_create('kazoo')
        self.assertEqual(k, k2)

class RawInstrumentMapTests(TestCase):
    def test_instrument_map(self):
        bagpipe = Instrument.find_or_create(instrument='bagpipe')
        self.assertTrue(str(bagpipe))
        r1 = RawInstrumentMap.objects.create(raw_instrument='Windbag',
                                             instrument=bagpipe)
        self.assertTrue(str(r1))
