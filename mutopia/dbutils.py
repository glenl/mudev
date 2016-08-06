"""
.. module:: dbutils
   :synopsis: Miscellaneous database utility functions

.. moduleauthor:: Glen Larsen <glenl.glx@gmail.com>

"""
from mutopia.models import Instrument, RawInstrumentMap

def instrument_match(instr):
    """Match a name to an internally known instrument.

    Given an instrument name of dubious quality, attempt to translate
    it to a pre-defined set of instrument names. The goal is smooth
    and accurate searches: we want users to be able to find music for
    a ukulele whether they search using the string *uke* or *ukulele*.

    If the given instrument matches one in the :class:`mutopia.Instrument`
    table, just return that name. Otherwise, look for match in
    :class:`mutopia.RawInstrumentMap`.

    :param str instr: The candidate instrument name
    :return: The matched (normalized) instrument
    :rtype: Instrument

    """
    try:
        instr = Instrument.objects.get(pk=instr.capitalize())
        return instr
    except Instrument.DoesNotExist:
        pass

    # else lookup in the translation map
    try:
        raw_instr = RawInstrumentMap.objects.get(raw_instrument__iexact=instr)
        return raw_instr.instrument
    except RawInstrumentMap.DoesNotExist:
        pass

    return None
