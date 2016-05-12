from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from mutopia.models import Piece

class LatestEntriesFeed(Feed):
    title = 'Latest Mutopia Project Updates'
    link = '/latest/'
    description = 'Updated and new pieces in the archive'

    def items(self):
        return Piece.objects.order_by('-date_published')[:10]

    def item_title(self, piece):
        return '{0}, {1}'.format(piece.title, piece.composer.byline())

    def item_description(self, piece):
        return 'Updated on {0}'.format(piece.date_published)

    def item_link(self, piece):
        return reverse('piece-info', args=[piece.pk])


class AtomLatestFeed(LatestEntriesFeed):
    feed_type = Atom1Feed
    subtitle = LatestEntriesFeed.description
