import os
import sys
import logging
import multiprocessing  # atexit exception
from setuptools import setup, find_packages

version = '0.5.1'

install_requires = ['setuptools',
                    'ptah >= 0.8.0',
                    'pyramid >= 1.3',
                    'zope.interface >= 3.8.0',
                    'SQLAlchemy',
                    ]

if sys.version_info[:2] in ((2,6),(2,7)):
    install_requires.extend(('simplejson',))

tests_require = install_requires + ['nose']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='ptahcms',
      version=version,
      description=('Ptah is a fast, fun, open source high-level '
                   'Python web development environment.'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: Implementation :: CPython",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Ptah Project',
      author_email='ptahproject@googlegroups.com',
      url='https://github.com/ptahproject/ptahcms/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require = dict(test=tests_require),
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True,
      zip_safe=False,
      package_data={'migrations': ['ptahcms/migrations/*.py']},
      entry_points={
          'pyramid.scaffold': [
              'ptahcms = ptahcms.scaffolds:PtahCMSProjectTemplate',
              ],
          },
      message_extractors={'ptahcms': [
        ('migrations/**', 'ignore', None),
        ('scaffolds/**', 'ignore', None),
        ('scripts/**', 'ignore', None),
        ('static/**', 'ignore', None),
        ('tests/**', 'ignore', None),
        ('*/tests/**', 'ignore', None),
        ('**.py', 'python', None),
        ('**.pt', 'lingua_xml', None),
      ]},
      )
