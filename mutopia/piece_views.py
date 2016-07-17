# -*- coding: utf-8 -*-
"""Views are functions that respond to HTTP requests, typically via a URL.
"""

from django.shortcuts import get_object_or_404, render
from mutopia.models import Piece, Composer, License, Style, Instrument
from mutopia.models import Collection, AssetMap, LPVersion
from mutopia.forms import KeySearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mutopia.utils import FTP_URL
import os.path
import requests


def piece_info(request, piece_id):
    """Given a piece identifier, render a page with extended Piece
    information.

    :param Request request: The HTTP request object
    :param int piece_id: the identifier (primary key) for a specific Piece
                     model instance.
    :return: An HTTP response containing a filled piece_info HTML page.

    """

    piece = get_object_or_404(Piece, pk=piece_id)

    asset = AssetMap.objects.get(piece=piece_id)
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'piece': piece,
        'asset': asset,
        'preview_image': '/'.join([FTP_URL, asset.folder, asset.name+'-preview.png',]),
        'instruments': piece.instruments.all(),
    }
    collection = piece.collection_set.all()
    if collection.count() > 0:
        context['collection'] = collection[0]
    return render(request, 'piece_info.html', context)


def log_info(request, piece_id):
    """Display the GIT change log for a particular piece.

    :param Request request: The HTTP request object
    :return: An HTML page containing the log information.

    """

    asset = AssetMap.objects.get(piece=piece_id)
    url = '/'.join([FTP_URL, asset.folder, asset.name+'.log',])
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'piece' : Piece.objects.get(pk=piece_id),
        'logfile': requests.get(url),
    }
    return render(request, 'piece_log.html', context)


def piece_by_instrument(request, instrument):
    """Render one or more pages of pieces composed for the given instrument.

    :param Request request: The HTTP request object
    :param str instrument: Instrument used to associate to a Piece.
    :return: A paginated page of pieces associated with the instrument.

    """
    pieces = Piece.objects.filter(instruments__pk=instrument)
    paginator = Paginator(pieces, 25)
    p = request.GET.get('page')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context = {
        'keyform': KeySearchForm(auto_id=False),
        'page': page,
        'instrument': instrument
    }
    return render(request, 'piece_instrument.html', context)


def piece_by_style(request, slug):
    """Render one or more pages of pieces composed for the given
    style. Note that the `slug` of the piece is passed so that the
    *actual style* will be valid as an HTML reference. The one style
    that is of particular interest is `Popular / Dance` which gets
    slugged as `popular-dance`.

    :param Request request: The HTTP request object
    :param str slug: The slug for this style.
    :return: A paginated page of pieces in the given style.
    """

    # Uses a slug so that "Popular / Dance" looks like a sane URL
    style = Style.objects.get(slug=slug)

    paginator = Paginator(Piece.objects.filter(style=style), 25)

    p = request.GET.get('page')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context = {
        'keyform': KeySearchForm(auto_id=False),
        'page': page,
        'style': style
    }
    return render(request, 'piece_style.html', context)


def piece_by_composer(request, composer):
    """Render one or more pages of pieces written by the given composer.

    :param Request request: The HTTP request object.
    :param str composer: The composer, formatted appropriately to
        associate with a Composer instance.
    :return: A paginated page of pieces by the given composer.

    """

    comp = Composer.objects.get(pk=composer)
    paginator = Paginator(Piece.objects.filter(composer=comp), 25)
    p = request.GET.get('page')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context = {
        'keyform': KeySearchForm(auto_id=False),
        'page': page,
        'composer': comp.rawstr()
    }
    return render(request, 'piece_composer.html', context)


def piece_by_version(request, version):
    """Render one or more pages of pieces transcribed by the given
    LilyPond style.

    :param Request request: The HTTP request object.
    :param str version: The LilyPond version.
    :return: A paginated page of pieces transcribed by this version.

    """

    v = LPVersion.objects.get(version=version)
    paginator = Paginator(Piece.objects.filter(version=v), 25)
    p = request.GET.get('page')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context = {
        'keyform': KeySearchForm(auto_id=False),
        'page': page,
        'version': version
    }
    return render(request, 'piece_version.html', context)


def collection_list(request, col_tag):
    """Display the collection associated with the given tag.

    :param Request request: The HTTP request object
    :param str col_tag: The tag for looking up the Collection.

    """

    col = Collection.objects.get(tag=col_tag)
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'title': col.title,
        'col_pieces': col.pieces.all()
    }
    return render(request, 'collection.html', context)
