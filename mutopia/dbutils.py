"""
.. module:: dbutils
   :platform: Linux
   :synopsis: Miscellaneous database utility functions

.. moduleauthor:: Glen Larsen <glenl.glx@gmail.com>

"""
from mutopia.models import Instrument, RawInstrumentMap

def instrument_match(instr):
    """Try to match directly to an instrument.

    :param instr: The candidate instrument name
    :type instr: str.
    :returns: string -- the matched (normalized) instrument

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
