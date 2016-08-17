"""This module contains the primary presentation views of the mutopia
   application.

"""

import time
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_safe
from django.db.models import Max
from django.shortcuts import HttpResponse, render
from django.template import loader
from django.db import ProgrammingError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from mutopia.models import Piece, Composer, License, Style, Instrument, Collection
from mutopia.models import SearchTerm
from mutopia.forms import KeySearchForm, AdvSearchForm, SearchInterval
from mutopia.forms import composer_choices, instrument_choices, style_choices

def homepage(request):
    """
    The home page for the site.

    """

    # The number of pieces referencing an instrument isn't provided in
    # Instrument so we annotate in an extra column using an aggregate,
    # then do a reverse sort to get the most frequent instrument at
    # the top of the list.
    instruments = Instrument.objects.filter(in_mutopia=True)
    instruments = instruments.annotate(count=Count('piece')).order_by('-count')

    # similar for composers and styles
    composers = Composer.objects.all()
    composers = composers.annotate(count=Count('piece')).order_by('-count')

    styles = Style.objects.filter(in_mutopia=True)
    styles = styles.annotate(count=Count('piece')).order_by('-count')

    context = {
        'active' : 'home',
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
    """
    The advanced search presents a form with many search options.

    """

    context = {
        'active' : 'search',
        'composers': composer_choices(),
        'instruments': instrument_choices(),
        'styles': style_choices(),
        'intervals': SearchInterval.INTERVAL_CHOICES,
    }
    return render(request, 'advsearch.html', context)


def legal(request):
    """
    The legal/license page is mostly HTML with a search form.
    """
    context = {
        'active' : 'legal',
        'keyform': KeySearchForm(auto_id=False),
    }
    return render(request, 'legal.html', context)


def contribute(request):
    """
    The contribute page display tables to help potential contributors
    build a correct header in their submissions.

    """

    context = {
        'keyform': KeySearchForm(auto_id=False),
        'active' : 'contribute',
        'composers': Composer.objects.all(),
        'licenses': License.objects.filter(active=True).order_by('name'),
        'styles': Style.objects.filter(in_mutopia=True)
    }
    return render(request, 'contribute.html', context)


def browse(request):
    """
    The browse page is a page of links to the following items,

      * Collections
      * Composers
      * Styles
      * Instruments

    """
    # TODO: this is a hacky way to split the columns. It works but
    # requires lots of messing about if the lists are restructured. It
    # also requires some fore-knowledge on the part of the template
    # since the presentation width is specified there.

    # collection
    col = Collection.objects.all()
    csplit = round(col.count()/2)
    # composers
    comp = Composer.objects.all()
    comps = round(comp.count()/3)
    # styles
    style = Style.objects.all()
    styles = round(style.count()/3)

    inst = Instrument.objects.filter(in_mutopia=True)
    insts = round(inst.count()/3)
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'active' : 'browse',
        'collections': (col[:csplit], col[csplit:],),
        'composers': (comp[:comps], comp[comps:(comps+comps)], comp[(comps+comps):],),
        'styles': (style[:styles], style[styles:(styles+styles)], style[(styles+styles):],),
        'instruments': (inst[:insts], inst[insts:(insts+insts)], inst[(insts+insts):],),
    }
    return render(request, 'browse.html', context)


def contact(request):
    """
    The contact page is HTML with a search form.
    """
    context = {
        'active' : 'contact',
        'keyform': KeySearchForm(auto_id=False),
    }
    return render(request, 'contact.html', context)


def key_results(request):
    """
    This responds to keyword search request (typically from the entry
    box on the jumbotron but could be anywhere. If there is more than
    one page, this routine may be re-entered to process other pages.

    """

    start_time = time.time()

    page = request.GET.get('page')
    if page is None:
        form = KeySearchForm(request.GET)
        if form.is_valid():
            # Uses session cookies to track the query between pages.
            request.session['keywords'] = form.cleaned_data['keywords']

    # If ther are no keywords here, the user entered nothing or the
    # form was not valid.
    keywords = request.session.get('keywords', '')

    try:
        query = SearchTerm.search(keywords)
    except ProgrammingError:
        context = {
            'active' : 'None',
            'message': 'Unable to parse keywords search terms',
            'keyform': KeySearchForm(),
        }
        return render(request, 'results.html', context)

    paginator = Paginator(query, 25)
    try:
        pieces = paginator.page(page)
    except PageNotAnInteger:
        # typically the first page of results
        pieces = paginator.page(1)
    except EmptyPage:
        pieces = paginator.page(paginator.num_pages)

    end_time = time.time()
    context = {
        'active' : 'None',
        'pieces': pieces,
        'keyform': KeySearchForm(),
        'pager': pieces,
        'keywords': keywords,
        'search_time': '%2.4g' % (end_time - start_time),
    }
    return render(request, 'results.html', context)


def adv_results(request):
    """
    Process the form from an advanced search.
    We expect to always get here from the advanced search page and
    always on a get, either from the submit button on the form or the
    paging navigation buttons.

      * On first search submission, load the request session dictionary
        from form values.

      * On subsequent paging calls, if any, form values are pulled from
        the session dictionary.

    """
    start_time = time.time()
    page = request.GET.get('page')
    if page is None:
        # reset session data
        for item in ['searchingfor', 'composer', 'style', 'instrument', 'lilyversion']:
            request.session[item] = ''
        request.session['time_delta'] = 0

        form = AdvSearchForm(request.GET)
        if form.is_valid():
            if len(form.cleaned_data['searchingfor']) > 0:
                request.session['searchingfor'] = form.cleaned_data['searchingfor']
            if len(form.cleaned_data['composer']) > 0:
                request.session['composer'] = form.cleaned_data['composer']
            if len(form.cleaned_data['style']) > 0:
                request.session['style'] = form.cleaned_data['style']
            if len(form.cleaned_data['instrument']):
                request.session['instrument'] = form.cleaned_data['instrument']
            if form.cleaned_data['lilyv']:
                # still, the user has to fill something in here
                if len(form.cleaned_data['lilyversion']) > 0:
                    request.session['lilyversion'] = form.cleaned_data['lilyversion']

            if form.cleaned_data['recent']:
                # Store the computed time delta in days, not the value
                # of recent. Note that 'timelength' and 'timeunit'
                # values should exist per form constraints.
                time_delta = form.cleaned_data['timelength']
                if form.cleaned_data['timeunit'] == SearchInterval.WEEK:
                    time_delta = 7 * time_delta
                request.session['time_delta'] = time_delta
        else:
            pass                # request session will be cleared

    # Now walk through the session variables to do the query and
    # filtering.
    if len(request.session['searchingfor']) > 0:
        query = SearchTerm.search(request.session['searchingfor'])
    else:
        query = Piece.objects.all()

    # Filter on composer, instrument, style, and LilyPond version
    if len(request.session['composer']) > 0:
        query = query.filter(composer=request.session['composer'])
    if len(request.session['style']) > 0:
        query = query.filter(style=request.session['style'])
    if len(request.session['instrument']) > 0:
        query = query.filter(instruments__pk=request.session['instrument'])
    if len(request.session['lilyversion']) > 0:
        query = query.filter(version__version__startswith=request.session['lilyversion'])

    # Finally, filter on delta time in days
    if request.session['time_delta'] > 0:
        time_delta = datetime.timedelta(days=request.session['time_delta'])
        target = datetime.date.today() - time_delta
        query = query.filter(date_published__gte=target)

    paginator = Paginator(query, 25)
    try:
        pager = paginator.page(page)
    except PageNotAnInteger:
        pager = paginator.page(1)
    except EmptyPage:
        pager = paginator.page(paginator.num_pages)

    end_time = time.time()
    context = {
        'active' : 'None',
        'pager' : pager,
        'pieces': pager,
        'search_time': '%2.4g' % (end_time - start_time),
    }
    return render(request, 'results.html', context)


@require_safe
def site_status(request):
    """A request to view the status of the site.

    Return various bits of information about a site in a JSON object.
    The following example retrieves the last mutopia piece id, ::

      import requests
      r = requests.head('http://<site>/status/')
      incoming = json.loads(r.content.decode('utf-8'))
      print(incoming['LastID'])

    :param request: HTTPRequest object
    :returns: response object with json content
    :rtype: JsonResponse

    """

    piecemax = Piece.objects.all().aggregate(Max('piece_id'))
    next_id = int(piecemax['piece_id__max']) + 1
    response = JsonResponse({'LastID': piecemax['piece_id__max']})
    return response


def handler404(_, template_name='404.html'):
    """
    Responds to pages that cannot be located on the server.
    """
    template = loader.get_template(template_name)
    response = HttpResponse(template.render({}))
    response.status_code = 404
    return response
