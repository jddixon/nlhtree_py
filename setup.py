#!/usr/bin/python3

# 'apt-get install python-dev' may be necessary to get .core

import re
from distutils.core import setup
__version__ = re.search("__version__\s*=\s*'(.*)'",
                        open('nlhtree/__init__.py').read()).group(1)

setup(name='nlhtree_py',
      version=__version__,
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      py_modules=[],
      packages=['nlhtree', ],
      scripts=[
          'nlhCheckInDataDir',
          'nlhCheckInUDir',
          'nlhPopulateDataDir',
          'nlhSaveToUDir',
      ]
      )
