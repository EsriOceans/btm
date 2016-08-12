""" tempdir.py: a contextual wrapper around tempfile. 'tempdir' on PyPI;
                inlined here for packaging reasons.

   https://bitbucket.org/another_thomas/tempdir/src/

   Author: Thomas Fenzl
   License: MIT
"""

from __future__ import with_statement
import gc
import os
import tempfile
import shutil
from functools import wraps
from contextlib import contextmanager


class TempDir(object):
    """ class for temporary directories
creates a (named) directory which is deleted after use.
All files created within the directory are destroyed
Might not work on windows when the files are still opened
"""
    def __init__(self, suffix="", prefix="tmp", basedir=None):
        self.name = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=basedir)

    def __del__(self):
        if "name" in self.__dict__:
            self.__exit__(None, None, None)

    def __enter__(self):
        return self.name

    def __exit__(self, *errstuff):
        return self.dissolve()

    def dissolve(self):
        """remove all files and directories created within the tempdir"""
        if self.name:
            self._rm()

        self.name = ""

    def _rm(self):
        try:
            # force garbage collection, ArcPy likes to keep holding
            # on to refs despite being out of scope. Testing shows
            # this only takes about 10ms, and prevents WindowsError exceptions.
            gc.collect()
            shutil.rmtree(self.name)
        except WindowsError as e:
            # abandon all hope -- arcpy won't give up the lock.
            pass

    def __str__(self):
        if self.name:
            return "temporary directory at: %s" % (self.name,)
        else:
            return "dissolved temporary directory"


@contextmanager
def in_tempdir(*args, **kwargs):
    """Create a temporary directory and change to it.
    """
    old_path = os.getcwd()
    try:
        with TempDir(*args, **kwargs) as t:
            os.chdir(t)
            yield t
    finally:
        os.chdir(old_path)


def run_in_tempdir(*args, **kwargs):
    """Make a function execute in a new tempdir.
    Any time the function is called, a new tempdir is created and destroyed.
    """
    def change_dird(fnc):
        @wraps(fnc)
        def wrapper(*funcargs, **funckwargs):
            with in_tempdir(*args, **kwargs):
                return fnc(*funcargs, **funckwargs)
        return wrapper
    return change_dird
