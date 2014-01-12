#!/usr/bin/env python

from distutils.core import setup
from jsondb import __version__

setup(name='jsondb',
      version=__version__,
      description='JSON db engine',
      author='Paul Ollivier',
      author_email='contact@paulollivier.fr',
      url='https://github.com/paulollivier/jsondb',
      packages=['jsondb',],
     )

