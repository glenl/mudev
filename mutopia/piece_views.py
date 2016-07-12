# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from mutopia.models import Piece, Composer, License, Style, Instrument
from mutopia.models import Collection, AssetMap, LPVersion
from mutopia.forms import KeySearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mutopia.utils import FTP_URL
import os.path
import requests


def piece_info(request, piece_id):
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
    asset = AssetMap.objects.get(piece=piece_id)
    url = '/'.join([FTP_URL, asset.folder, asset.name+'.log',])
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'piece' : Piece.objects.get(pk=piece_id),
        'logfile': requests.get(url),
    }
    return render(request, 'piece_log.html', context)


def piece_by_instrument(request, instrument):
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
    col = Collection.objects.get(tag=col_tag)
    context = {
        'keyform': KeySearchForm(auto_id=False),
        'title': col.title,
        'col_pieces': col.pieces.all()
    }
    return render(request, 'collection.html', context)
