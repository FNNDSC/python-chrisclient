
from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
      name             =   'python-chrisclient',
      version          =   '2.8.2',
      description      =   '(Python) client for the ChRIS API',
      long_description =   readme,
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/python-chrisclient',
      packages         =   ['chrisclient'],
      install_requires =   ['requests>=2.21.0', 'collection-json>=0.1.1', 'pudb', 'pfstate', 'pfmisc', 'webob'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['bin/chrisclient', 'bin/chrispl-run', 'bin/chrispl-search'],
      license          =   'MIT',
      zip_safe         =   False,
      python_requires  =   '>=3.7'
)
