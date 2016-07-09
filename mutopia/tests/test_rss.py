from django.test import TestCase
from .utilities import make_piece
from mutopia.rss import AtomLatestFeed
from datetime import date

class RSSTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        p = make_piece()
        p.date_published = date.today()
        p.title = 'RSS Test'
        p.save()

    def test_rss(self):
        feed = AtomLatestFeed()
        self.assertEqual(feed.items()[0].title, 'RSS Test')
