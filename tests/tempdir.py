""" tempdir.py: a contextual wrapper around tempfile. 'tempdir' on PyPI; inlined here for packaging reasons.
   https://bitbucket.org/another_thomas/tempdir/src/fa6a07ad0024f0d96d1cedab63792931e9b744a4/tempdir.py?at=default

   Author: Thomas Fenzl
   License: MIT
"""

from __future__ import with_statement
import os
import tempfile
import time
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
        # slow down, champ: arcpy is slow to give up access, let if have a little breather.
        #time.sleep(0.5) 
        return self.dissolve()

    def dissolve(self):
        """remove all files and directories created within the tempdir"""
        if self.name:
            shutil.rmtree(self.name)
        self.name = ""

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
