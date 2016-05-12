# -*- coding: utf-8 -*-
from django import forms
from mutopia.models import Composer, Instrument, Style

class KeySearchForm(forms.Form):
    """ A form for the one-line search box on the jumbotron"""
    keywords = forms.CharField(max_length=100,
                               required=False,
                               label=False,
                               widget=forms.TextInput(
                                   attrs={'autofocus':'autofocus',
                                          'class': 'form-control',
                                          'placeholder': 'Search for ...',
                                          'name': 'keywords'
                                   })
    )


def composer_choices():
    """ A tuple list of the choices for composers """
    comps = []
    comps.append( ('','any composer') )
    for c in Composer.objects.all():
        comps.append( (c.composer, c.description) )
    return comps


def instrument_choices():
    """ A tuple list of the choices for instruments """
    instr = []
    instr.append( ('','any instrument') )
    for c in Instrument.objects.filter(in_mutopia=True):
        instr.append( (c.instrument, c.instrument) )
    return instr


def style_choices():
    """ A tuple list of the choices for styles """
    styles = []
    styles.append( ('','any style') )
    for c in Style.objects.filter(in_mutopia=True):
        styles.append( (c.style, c.style) )
    return styles


class SearchInterval:
    WEEK = 'WEEK'
    DAY = 'DAY'
    INTERVAL_CHOICES = (
        (WEEK, 'week(s)'),
        (DAY,  'day(s)'),
    )

class AdvSearchForm(forms.Form):
    """This is the full-page search form returned as a main menu item. The
    form displays the keyword text entry box with optional filters.
    """

    searchingfor = forms.CharField(max_length=100, required=False)

    # narrow search by these composer, instrument, or style
    composer = forms.ChoiceField(composer_choices, required=False)
    instrument = forms.ChoiceField(instrument_choices, required=False)
    style = forms.ChoiceField(style_choices, required=False)

    # is this piece for solo instrument?
    solo = forms.BooleanField(required=False)

    # updated in the past n weeks or days
    recent = forms.BooleanField(required=False)
    timelength = forms.IntegerField(required=False)
    timeunit = forms.ChoiceField(choices=SearchInterval.INTERVAL_CHOICES, required=False)

    # created using a specific version of LilyPond
    lilyv = forms.BooleanField(required=False)
    lilyversion = forms.CharField(max_length=12, required=False)
