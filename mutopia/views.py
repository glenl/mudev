# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db import connection, ProgrammingError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mutopia.models import Piece, Composer, License, Style, Instrument, Collection
from mutopia.forms import KeySearchForm, AdvSearchForm, SearchInterval
from mutopia.forms import composer_choices, instrument_choices, style_choices
from mutopia.forms import SearchInterval
import re
import time
import datetime

def homepage(request):
    """The home page for the site"""
    instruments = []
    for i in Instrument.objects.filter(in_mutopia=True):
        instruments.append((i.instrument,
                            Piece.objects.filter(instruments=i).count()))
    instruments = sorted(instruments, key=lambda x: x[1], reverse=True)

    composers = []
    for c in Composer.objects.all():
        composers.append((c, Piece.objects.filter(composer=c).count()))
    composers = sorted(composers, key=lambda x: x[1], reverse=True)

    styles = []
    for s in Style.objects.all():
        styles.append((s, Piece.objects.filter(style=s).count()))
    styles = sorted(styles, key=lambda x: x[1], reverse=True)

    context = {
        'nav_home' : 'active',
        'keyform': KeySearchForm(auto_id=False),
        'latest_list' : Piece.objects.order_by('-piece_id')[:10],
        'instruments' : instruments[:18],
        'composers' : composers[:18],
        'styles' : styles[:18],
        'pieces' : Piece.objects.count(),
        'collections' : Collection.objects.all()[:14],
    }
    return render(request, 'index.html', context)


def adv_search(request):
    context = {
        'nav_search': 'active',
        'composers': composer_choices(),
        'instruments': instrument_choices(),
        'styles': style_choices(),
        'intervals': SearchInterval.INTERVAL_CHOICES,
    }
    return render(request, 'advsearch.html', context);


def legal(request):
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'nav_legal': 'active'
    }
    return render(request, 'legal.html', context)


def contribute(request):
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'nav_contribute': 'active',
        'composers': Composer.objects.all(),
        'licenses': License.objects.filter(active=True).order_by('name'),
        'styles': Style.objects.filter(in_mutopia=True)
    }
    return render(request, 'contribute.html', context)


def browse(request):
    # collection
    c = Collection.objects.all()
    csplit = round(c.count()/2)
    # composers
    comp = Composer.objects.all()
    comps = round(comp.count()/3)
    # styles
    s = Style.objects.all()
    ss = round(s.count()/3)

    inst = Instrument.objects.filter(in_mutopia=True)
    insts = round(inst.count()/3)
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'nav_browse': 'active',
        'collections': (c[:csplit], c[csplit:],),
        'composers': (comp[:comps], comp[comps:(comps+comps)], comp[(comps+comps):],),
        'styles': (s[:ss], s[ss:(ss+ss)], s[(ss+ss):],),
        'instruments': (inst[:insts], inst[insts:(insts+insts)], inst[(insts+insts):],),
    }
    return render(request, 'browse.html', context)


def contact(request):
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'nav_contact': 'active'
    }
    return render(request, 'contact.html', context)


def title_search(keywords):
    """Given keywords, search for a containment match in titles
    """
    p = re.compile(r'\W+')
    kws = p.split(keywords)
    q = Piece.objects.filter(title__icontains=kws[0])
    kws = kws[1:]
    for kw in kws:
        q = q.filter(title__icontains=kw)
    return q


_SQLITE_FTSQ = """SELECT piece_id FROM muPieceKeys \
 WHERE muPieceKeys MATCH '%{0}'"""

_PG_FTSQ = """SELECT piece_id FROM mu_search_table \
WHERE document @@ to_tsquery('english', '{0}')"""

def fts_search(keywords):
    """Given keywords, search using FTS.
    Because FTS is not a supported feature of django and SQLite, it is
    faked here by using a manual query that returns keys for the
    muPiece table (model.Piece). This gets translated into a QuerySet
    of Pieces using a filter.
    """
    try:
        cursor = connection.cursor()
        if re.search('[\(&\)\|\-!]', keywords) is not None:
            # the user is using fts query logic so use the string as is
            cursor.execute(_PG_FTSQ.format(keywords))
        else:
            # Assume the user wants to logically AND all keywords
            k = keywords.split()
            cursor.execute(_PG_FTSQ.format(' & '.join(k)))

        # Get the results as a simple list of ids for the filter
        results = [ row[0] for row in cursor.fetchall() ]
        return Piece.objects.filter(pk__in=results)
    except ProgrammingError:
        return None


def key_results(request):
    if request.method == 'GET':
        form = KeySearchForm(request.GET)
        if form.is_valid():
            start_time = time.time()
            context = { 'page': None,
                        'keyform': form,
            }
            keywords = form.cleaned_data['keywords']
            try:
                q = fts_search(keywords)
            except ProgrammingError:
                context['message'] = 'Unable to parse keywords search terms'

            if q is None or q.count() < 1:
                context['message'] = 'No pieces were returned with these search terms'
            else:
                paginator = Paginator(q, 25)
                page = request.GET.get('page')
                try:
                    page = paginator.page(page)
                except PageNotAnInteger:
                    page = paginator.page(1)
                except EmptyPage:
                    page = paginator.page(paginator.num_pages)

                context['page'] = page

            end_time = time.time()
            context['keywords'] = keywords
            context['search_time'] = '%2.4g' % (end_time - start_time)
            return render(request, 'results.html', context)

    # default is to return to page?
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


def adv_results(request):
    """Process the form from an advanced search.
    """
    if request.method == 'GET':
        form = AdvSearchForm(request.GET)
        if form.is_valid():
            start_time = time.time()

            # Using fts with sqlite requires we process the keyword entry first
            keywords = form.cleaned_data['searchingfor']
            if len(keywords) > 0:
                q = fts_search(keywords)
            else:
                q = Piece.objects.all()

            # process the composer, instrument, and style choices if any
            if form.cleaned_data['composer']:
                q = q.filter(composer=form.cleaned_data['composer'])
            if form.cleaned_data['style']:
                q = q.filter(style=form.cleaned_data['style'])
            if form.cleaned_data['instrument']:
                q = q.filter(instruments__pk=form.cleaned_data['instrument'])

            # If the user requested a time-based search, filter that here.
            if form.cleaned_data['recent']:
                td = datetime.timedelta(days=form.cleaned_data['timelength'])
                if form.cleaned_data['timeunit'] == SearchInterval.WEEK:
                    td = 7 * td
                target_date = datetime.date.today() - td
                q = q.filter(date_published__gte=target_date)

            # Filter on LilyPond versions by searching for versions
            # starting with the given value.
            if form.cleaned_data['lilyv']:
                q = q.filter(version__version__startswith=form.cleaned_data['lilyversion'])

            paginator = Paginator(q, 25)
            page = request.GET.get('page')
            try:
                page = paginator.page(page)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)


            # Force evaluation here so we get the correct search time.
            end_time = time.time()
            context = { 'page' : page,
                        'keywords': keywords,
                        'search_time': '%2.4g' % (end_time - start_time),
            }
            return render(request, 'results.html', context)

    # default is to return to page?
    return HttpResponseRedirect('/')


def page_not_found(request):
    response = render_to_response('404.html',
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
