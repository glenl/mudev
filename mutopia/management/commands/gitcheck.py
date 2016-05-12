from django.core.management.base import BaseCommand, CommandError
from mutopia.models import Piece


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
    help = 'Check length of source field'


    def handle(self, *args, **options):
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

        self.stdout.write('RDF files to process: {0}'.format(len(rdfset)))
