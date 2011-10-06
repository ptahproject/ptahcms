import sys, os
from setuptools import setup, find_packages

version='0.1dev'

setup(name='ptah',
      version=version,
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/ptah/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      install_requires = ['setuptools',
                          'memphis',
                          'pyramid_sqla',
                          'pyramid_beaker',
                          'sqlalchemy',
                          'zope.interface',
                          'repoze.sendmail',
                          'Pygments',
                          ],
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = ptah'],
        'paste.app_factory': [
            'app = ptah:make_wsgi_app'],
        },
      )
