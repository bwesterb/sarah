#!/usr/bin/env python

from setuptools import setup, find_packages
from get_git_version import get_git_version
import os, os.path

def find_package_data():
    base = os.path.join(os.path.dirname(__file__), 'src')
    s, r = ['.'], []
    while s:
        p = s.pop()
        for c in os.listdir(os.path.join(base, p)):
            if os.path.isdir(os.path.join(base, p, c)):
                s.append(os.path.join(p, c))
            elif c.endswith('.mirte'):
                r.append(os.path.join(p, c))
    return r

setup(name='sarah',
      version=get_git_version(),
      description='Library with miscellaneous functionality',
      author='Bas Westerbaan',
      author_email='bas@westerbaan.name',
      url='http://github.com/bwesterb/sarah/',
      packages=['sarah'],
      zip_safe=False,
      package_dir={'sarah': 'src'},
      package_data={'sarah': find_package_data()},
      install_requires = ['docutils>=0.3',
                          'mirte>=0.1.2'],
      )
