"""
Useful functions for loading the latest version
of a typelib given just it's IID.

"""

from win32com.client import gencache
from _winreg import OpenKey, HKEY_CLASSES_ROOT, QueryInfoKey, EnumKey

def GetTypelibVersions(IID):
    """
    Returns the list of installed versions of a
    given typelib. Versions are returned as a list
    of two element tuples of the form (major, minor)
    where major, minor are integers.

    """
    versions = []
    with OpenKey(HKEY_CLASSES_ROOT, 'Typelib\\' + IID) as key:
        subkeycount, _, _ = QueryInfoKey(key)

        for i in range(subkeycount):
            rawversion = EnumKey(key, i)

            # We're only interested in subkeys of the form
            # MAJORVERSION.MINORVERSION
            if rawversion.count('.') != 1:
                continue

            rawmajor, rawminor = rawversion.split('.')
            # Versions are expressed in hex.
            major, minor = int(rawmajor, 16), int(rawminor, 16)
            versions.append((major, minor))

    return versions

def GetTypelibLatestVersion(IID):
    """
    Returns a 2 element tuple containing the latest
    major and minor version of the given typelib. Returns
    (None, None) if the typelib wasn't found.

    """
    versions = GetTypelibVersions(IID)
    versions.sort()

    return versions[-1] if versions else (None, None)

def EnsureLatestVersion(IID):
    """
    Returns the win32com wrapped module for the
    latest version of the given typelib.

    The Python wrapper will be generated if it
    doesn't already exist.

    """
    major, minor = GetTypelibLatestVersion(IID)

    if major:
        return gencache.EnsureModule(IID, 0, major, minor)
    else:
        return None
