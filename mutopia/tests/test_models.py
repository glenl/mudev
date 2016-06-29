import re
from django.test import TestCase
from django.utils.text import slugify
from mutopia.models import Composer, Contributor, Style, LPVersion, Piece
from .utilities import make_piece

class ComposerTests(TestCase):
    def test_composer(self):
        homer = Composer.objects.create(composer='SimpsonH', description='Homer Simpson(1999--)')
        self.assertTrue(isinstance(homer, Composer))
        self.assertEqual(homer.__str__(), homer.composer)
        self.assertFalse(re.search('[0-9]', homer.rawstr()))


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
        self.assertEqual(sluggable.__str__(), sluggable.style)
        self.assertNotEqual(sluggable.__str__(), sluggable.slug)


class LPVersionTests(TestCase):
    def test_version(self):
        v1 = LPVersion.find_or_create('1.2.3')
        self.assertTrue(isinstance(v1, LPVersion))
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
