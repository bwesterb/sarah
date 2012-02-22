#!/usr/bin/env python

from setuptools import setup, find_packages, findall
from get_git_version import get_git_version

setup(name='sarah',
      version=get_git_version(),
      description='Library with miscellaneous functionality',
      author='Bas Westerbaan',
      author_email='bas@westerbaan.name',
      url='http://github.com/bwesterb/sarah/',
      packages=['sarah'],
      zip_safe=False,
      package_dir={'sarah': 'src'},
      package_data={
          'sarah': [f for f in findall('sarah') if f.endswith('.mirte')]},
      install_requires = ['docutils>=0.3',
                          'mirte>=0.1.1'],
      )
