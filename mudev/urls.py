"""mudev URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/

"""

from django.conf.urls import include, url
from django.contrib import admin
from mutopia import views, piece_views
from mutopia.rss import LatestEntriesFeed, AtomLatestFeed
from django.conf.urls import handler404

piece_patterns = [
    url(r'^info/(?P<piece_id>[0-9]+)/$',
        piece_views.piece_info,
        name='piece-info'),
    url(r'^log/(?P<piece_id>[0-9]+)/$',
        piece_views.log_info,
        name='piece-log'),
    url(r'^instrument/(?P<instrument>[\w]+)/$',
        piece_views.piece_by_instrument,
        name='piece-by-instrument'),
    url(r'^style/(?P<slug>[\-\w]+)/$',
        piece_views.piece_by_style,
        name='piece-by-style'),
    url(r'^composer/(?P<composer>[\-\w]+)/$',
        piece_views.piece_by_composer,
        name='piece-by-composer'),
    url(r'^collection/(?P<col_tag>[\w]+)/$',
        piece_views.collection_list,
        name='collection-list'),
    url(r'^version/(?P<version>[0-9A-Za-z\.]+)/$',
        piece_views.piece_by_version,
        name='piece-by-version'),
]

urlpatterns = [
    url(r'^$',
        views.homepage,
        name='home'),
    url(r'^browse/',
        views.browse,
        name='browse'),
    url(r'^search/',
        views.adv_search,
        name='search'),
    url(r'^legal/',
        views.legal,
        name='legal'),
    url(r'^contribute/',
        views.contribute,
        name='contribute'),
    url(r'^contact/',
        views.contact,
        name='contact'),
    url(r'^piece/', include(piece_patterns)),
    url(r'key-results/',
        views.key_results,
        name='key-results'),
    url(r'adv-results/',
        views.adv_results,
        name='adv-results'),
    url(r'^admin/', admin.site.urls),
    url(r'latest/rss/$',
        LatestEntriesFeed(),
        name='latest-rss'),
    url(r'latest/atom/$',
        AtomLatestFeed(),
        name='latest-atom'),
    url(r'status/$',
        views.site_status,
        name='site-status'),
]

handler404 = 'mutopia.views.handler404'
