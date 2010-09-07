#!/usr/bin/env python

from setuptools import setup

setup(name='sarah',
      version='0.1.0a1',
      description='Library with miscellaneous functionality',
      author='Bas Westerbaan',
      author_email='bas@westerbaan.name',
      url='http://github.com/bwesterb/sarah/',
      packages=['sarah'],
      zip_safe=False,
      package_dir={'sarah': 'src'},
      install_requires = ['docutils>=0.3',
			  'mirte>=0.1.0a1']
      )
