import re
import os
import os.path
from datetime import date
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from django.db import transaction
from mutopia.models import Composer, Style, Piece, Instrument, Contributor
from mutopia.models import LPVersion, RawInstrumentMap, UpdateMarker
from mutopia.models import AssetMap, License
from mutopia.utils import GITHUB_REPOS, FTP_URL, id_from_footer
from subprocess import check_output
from rdflib import Graph, URIRef, Namespace, URIRef
from rdflib.term import Literal
import requests
from requests.auth import HTTPBasicAuth

MP = Namespace('http://www.mutopiaproject.org/piece-data/0.1/')
git_headers = {'Accept' : 'application/vnd.github.v3+json'}

def instrument_match(w):
    """try a match directly to an instrument"""
    try:
        t = Instrument.objects.get(pk=w.capitalize())
        return t
    except Instrument.DoesNotExist:
        pass

    # else lookup in the translation map
    try:
        r = RawInstrumentMap.objects.get(raw_instrument__iexact=w)
        return r.instrument
    except RawInstrumentMap.DoesNotExist:
        pass

    return None


def commits_since(auth, since_date):
    """Request a list of repository commits from the given date as a
       JSON structure using the github API.
    """
    req = '/'.join([GITHUB_REPOS, 'commits?since={0}'.format(since_date),])
    r = requests.get(req, auth=auth, headers=git_headers)
    if (r.status_code != requests.codes.ok):
        r.raise_for_status()
    return r.json()


def resolve_rdf(fnm):
    """Given a filename relative to the top of the repository, figure
    out if an RDF file can be associated with it.
    """
    has_lys = False
    if fnm.startswith('ftp') and fnm.endswith('.ly'):
        t = []
        fparts = fnm.split(os.sep)
        fparts.pop(0)
        while True:
            p = fparts.pop(0)
            if p.endswith('.ly') or p.endswith('-lys'):
                has_lys = True
                break
            t.append(p)
        t.append(t[len(t)-1] + '.rdf')
        # rejoin parts with a forward-slash
        return ('/'.join(t), has_lys)
    else:
        return None


class Command(BaseCommand):
    help = """Database load utility for the mutopia application.
    """

    def update_instruments(self):
        """Update the instrument list for any piece that is missing
        instruments.
        """
        pat = re.compile('\W+')
        pieces = Piece.objects.all().filter(instruments__isnull=True)
        for p in pieces:
            mlist = set()
            ilist = pat.split(p.raw_instrument)
            for i in ilist:
                instrument = i.strip()
                if len(instrument) < 3: next
                t = instrument_match(instrument)
                if t:
                    mlist.add(t)
            if len(mlist) > 0:
                self.stdout.write('  {0}: instrument {1}'.format(p.piece_id,mlist))
                for instr in mlist:
                    p.instruments.add(instr)


    def update_pieces(self):
        # get all RDF specs with a null piece reference
        rmap = AssetMap.objects.all().filter(piece__isnull=True)
        for r in rmap:
            path = '/'.join([FTP_URL, r.folder, r.name+'.rdf',])
            graph = Graph().parse(URIRef(path))
            # Since we know the composer is required (which we have
            # from the spec) we can get the subject.
            mp_subj = graph.value(subject=None,
                                  predicate=MP.composer,
                                  object=Literal(r.get_composer()))

            # A footer isn't stored in the database but its bit parts are.
            footer = graph.value(mp_subj, MP.id)
            if footer is None:
                self.stderr.write('Failed to get footer from {0}'.format(path))
                break
            (pubdate, mutopia_id) = id_from_footer(footer)
            pdvec = [ int(x) for x in pubdate.split('/') ]

            # Determine if this is an update or a new piece
            piece = None
            status = None
            comp = Composer.objects.get(composer=graph.value(mp_subj, MP.composer))
            try:
                piece = Piece.objects.get(pk=mutopia_id)
                piece.title = graph.value(mp_subj, MP.title)
                piece.composer = comp
                status = 'update'
            except Piece.DoesNotExist:
                piece = Piece(piece_id = mutopia_id,
                              title = graph.value(mp_subj, MP.title),
                              composer = comp)
                status = 'new'

            # fill out the remainder of piece
            piece.style = Style.objects.get(pk=graph.value(mp_subj,MP.style))
            piece.raw_instrument = graph.value(mp_subj, MP['for'])
            piece.license = License.objects.get(name=graph.value(mp_subj, MP.licence))
            # use routines to get maintainer and version because we
            # might have to create them on the fly
            piece.maintainer = Contributor.find_or_create(
                graph.value(mp_subj, MP.maintainer),
                graph.value(mp_subj, MP.maintainerEmail),
                graph.value(mp_subj, MP.maintainerWeb))
            piece.version = LPVersion.find_or_create(
                graph.value(mp_subj, MP.lilypondVersion))
            piece.lyricist = graph.value(mp_subj, MP.lyricist)
            piece.date_composed = graph.value(mp_subj, MP.date)
            piece.date_published = date(pdvec[0], pdvec[1], pdvec[2])
            piece.source = graph.value(mp_subj, MP.source)
            piece.moreinfo = graph.value(mp_subj, MP.moreInfo)
            piece.opus = graph.value(mp_subj, MP.opus)
            piece.save()
            r.piece = piece
            r.save()
            self.stdout.write('  {0}: {1}'.format(status, piece))


    def rdfset_since(self, auth, marker):
        rdfset = set()
        for item in commits_since(auth, marker):
            br = requests.get('/'.join([GITHUB_REPOS, 'commits', item['sha'], ]),
                              auth=auth,
                              headers=git_headers)
            if (br.status_code == requests.codes.ok):
                comm_item = br.json()
                for files in comm_item['files']:
                    rdftuple = resolve_rdf(files['filename'])
                    if rdftuple is not None:
                        rdfset.add(rdftuple)
            else:
                print('Oops, got status code {0}'.format(r.status_code))
        return rdfset


    def update_assets(self, rdfset):
        self.stdout.write('RDF files to process: {0}'.format(len(rdfset)))
        for s in rdfset:
            (folder,name) = os.path.split(s[0])
            name = name[:name.rfind('.')]
            try:
                # if the RDF exists in the map, it is an update
                asset = AssetMap.objects.get(folder=folder)
                if asset.has_lys != s[1]:
                    self.stdout.write('  Asset "{0}" is now {1}'.format(s[0], s[1]))
                    asset.has_lys = s[1]
                asset.piece = None
                asset.save()
                self.stdout.write(' [update] {0}'.format(s))
            except AssetMap.DoesNotExist:
                # New entry in the archive
                asset = AssetMap(folder=folder, name=name, has_lys=s[1])
                asset.save()
                self.stdout.write(' [new] {0}'.format(s))


    def add_arguments(self, parser):
        parser.add_argument('-t', '--token',
                            dest='token',
                            help='github personal token')
        parser.add_argument('-u', '--user',
                            dest='user',
                            help='github username')
        parser.add_argument('--skip-github',
                            dest='github',
                            action='store_false',
                            default=True)
        parser.add_argument('--skip-asset-write',
                            dest='asset_write',
                            action='store_false',
                            default=True)


    def handle(self, *args, **options):
        marker = UpdateMarker.objects.latest('updated_on')

        auth = None
        if options['user']:
            if options['token']:
                auth = HTTPBasicAuth(options['user'], options['token'])
            else:
                self.stdout.write('User given but no token, will try with None anyway.')

        if options['github']:
            self.stdout.write('Getting commits from github since {0}'.format(marker))
            self.stdout.write('  Patience...')
            rdfset = self.rdfset_since(auth, marker)
            if options['asset_write']:
                self.update_assets(rdfset)
            else:
                for rdf in rdfset:
                    self.stdout.write('  skipped {0}'.format(rdf))

            new_marker = UpdateMarker(updated_on=timezone.now())
            new_marker.save()

        with transaction.atomic():
            self.stdout.write('Processing new or updated RDF files')
            self.update_pieces()
            self.update_instruments()
