# -*- coding: utf-8 -*-
import os
import re

MUTOPIA_BASE = 'MUTOPIA_BASE'
MUTOPIA_WEB = 'MUTOPIA_WEB'
MUTOPIA_URL = 'http://www.mutopiaproject.org'
FTP_URL = MUTOPIA_URL + '/ftp'
GITHUB_REPOS = 'https://api.github.com/repos/MutopiaProject/MutopiaProject'

__all__ = [
    'MUTOPIA_BASE',
    'MUTOPIA_WEB',
    'MUTOPIA_URL',
    'FTP_URL',
    'GITHUB_REPOS',
    'id_from_footer',
]


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.
    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """Returns the singleton instance.

        Returns:
            Upon its first call, it creates a new instance of the
            decorated class and calls its `__init__` method. On all
            subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


_FOOT_PAT = re.compile("Mutopia-([0-9/]+)-([0-9]+)$")
def id_from_footer(footer):
    """Parse a Mutopia footer string.

    Args:
        footer: the mutopia footer string from the header

    Returns:
        A tuple containing the pertinent footer information or None
        if the regular expression fails. For example,

        Mutopia-2016/20/12-33 ==> ("2016/20/12", "33")
        Mutopia-2016/20/12-AB ==> None
    """
    if footer:
        fmat = _FOOT_PAT.search(footer)
        if fmat:
            return (fmat.group(1),fmat.group(2))
    return None
