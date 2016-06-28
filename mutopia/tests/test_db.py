from django.test import TestCase
from mutopia.models import Instrument, RawInstrumentMap
from mutopia.dbutils import instrument_match

class RawInstrumentTestCase(TestCase):
    def setUp(self):
        g = Instrument.objects.create(instrument='Guitar')
        u = Instrument.objects.create(instrument='Ukulele')
        RawInstrumentMap.objects.create(raw_instrument='axe', instrument=g)
        RawInstrumentMap.objects.create(raw_instrument='guitarre', instrument=g)
        RawInstrumentMap.objects.create(raw_instrument='uke', instrument=u)

    def test_can_translate(self):
        guitar = instrument_match('axe')
        self.assertEqual(guitar.instrument, 'Guitar')
        guitar = instrument_match('guitar')
        self.assertEqual(guitar.instrument, 'Guitar')
        guitar = instrument_match('guitarre')
        self.assertEqual(guitar.instrument, 'Guitar')
        uke = instrument_match('uke')
        self.assertEqual(uke.instrument, 'Ukulele')
        uke = instrument_match('uk')
        self.assertEqual(uke, None)
