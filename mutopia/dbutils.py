"""
.. module:: dbutils
   :platform: Linux
   :synopsis: Miscellaneous database utility functions

.. moduleauthor:: Glen Larsen <glenl.glx@gmail.com>

"""
from mutopia.models import Instrument, RawInstrumentMap

def instrument_match(instr):
    """Given an instrument name of dubious quality, attempt to
    normalize the name to a pre-defined set of instrument names. The
    goal is to make searches go more smoothly in a site package. We
    want users to be able to find music for a ukulele whether they
    search using the string *uke* or *ukulele*.

    If the given instrument matches one in the :class:`mutopia.Instrument`
    table, just return that name. Otherwise, look for match in
    :class:`mutopia.RawInstrumentMap`.

    :param str instr: The candidate instrument name
    :return: The matched (normalized) instrument
    :rtype: str

    """
    try:
        t = Instrument.objects.get(pk=instr.capitalize())
        return t
    except Instrument.DoesNotExist:
        pass

    # else lookup in the translation map
    try:
        r = RawInstrumentMap.objects.get(raw_instrument__iexact=instr)
        return r.instrument
    except RawInstrumentMap.DoesNotExist:
        pass

    return None
