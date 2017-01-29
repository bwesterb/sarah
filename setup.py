#!/usr/bin/env python

from setuptools import setup
import os
import os.path


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


base_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_path, 'README.rst')) as f:
    with open(os.path.join(base_path, 'CHANGES.rst')) as g:
        long_description = '{0}\n{1}'.format(f.read(), g.read())


setup(name='sarah',
      version='0.1.4',
      description='Library with miscellaneous functionality',
      long_description=long_description,
      author='Bas Westerbaan',
      author_email='bas@westerbaan.name',
      url='http://github.com/bwesterb/sarah/',
      packages=['sarah'],
      zip_safe=False,
      package_dir={'sarah': 'src'},
      package_data={'sarah': find_package_data()},
      install_requires=['docutils>=0.3',
                        'mirte>=0.1.2',
                        'six>=1.2'],
      )

# vim: et:sta:bs=2:sw=4:
