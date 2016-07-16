from django.core.management.base import BaseCommand, CommandError
from mutopia.models import SearchTerm
import re

class Command(BaseCommand):
    help = 'build and load the fts tables for PostGreSQL'

    def add_arguments(self, parser):
        parser.add_argument('--refresh',
                            action='store_true',
                            dest='refresh',
                            default=False,
                            help='refresh materialized view only')

    def handle(self, *args, **options):
        if options['refresh']:
            SearchTerm.refresh_view()
        else:
            SearchTerm.rebuild_view()
            SearchTerm.refresh_view()
