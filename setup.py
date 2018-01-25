#!/usr/bin/python3
# nlhtree_py/setup.py

""" Setuptools project configuration for nlhtree_py. """

from os.path import exists
from setuptools import setup

LONG_DESC = None
if exists('README.md'):
    with open('README.md', 'r') as file:
        LONG_DESC = file.read()

setup(name='nlhtree_py',
      version='0.7.17',
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      long_description=LONG_DESC,
      packages=['nlhtree'],
      package_dir={'': 'src'},
      py_modules=[],
      include_package_data=False,
      zip_safe=False,
      scripts=['src/nlh_check_in_data_dir', 'src/nlh_check_in_u_dir',
               'src/nlh_populate_data_dir', 'src/nlh_save_to_u_dir'],
      description='data structure for representing directory and contents',
      url='https://jddixon.github.io/nlhtree_py',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 2.7',
          'Programming Language :: Python 3.3',
          'Programming Language :: Python 3.4',
          'Programming Language :: Python 3.5',
          'Programming Language :: Python 3.6',
          'Programming Language :: Python 3.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],)
