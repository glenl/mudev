from django.test import TestCase
from mutopia.models import Instrument, RawInstrumentMap
from mutopia.dbutils import instrument_match

class RawInstrumentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.guitar = Instrument.objects.create(instrument='Guitar')
        cls.ukulele = Instrument.objects.create(instrument='Ukulele')
        RawInstrumentMap.objects.create(raw_instrument='axe', instrument=cls.guitar)
        RawInstrumentMap.objects.create(raw_instrument='uke', instrument=cls.ukulele)

    def test_can_translate(self):
        g = instrument_match('axe')
        self.assertEqual(g, self.guitar)
        g = instrument_match('guitar')
        self.assertEqual(g, self.guitar)
        uke = instrument_match('uke')
        self.assertEqual(uke, self.ukulele)
        uke = instrument_match('uk')
        self.assertEqual(uke, None)
