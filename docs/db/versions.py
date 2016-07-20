from django.core.management.base import BaseCommand
from mutopia.models import LPVersion
from django.db.models import Count

class Command(BaseCommand):
    help = 'Version counts'

    def handle(self, *args, **options):
        versions = LPVersion.objects.all()
        vc = versions.annotate(
            count=Count('piece')).order_by('-count')
        for v in vc[:12]:
            self.stdout.write(
                '{0:>8} : {1}'.format(v.version, v.count))
