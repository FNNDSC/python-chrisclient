import sys

# Make sure we are running python3.5+
if 10 * sys.version_info[0] + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'python-chrisclient',
      version          =   '2.2.6',
      description      =   '(Python) client for the ChRIS API',
      long_description =   readme(),
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/python-chrisclient',
      packages         =   ['chrisclient'],
      install_requires =   ['requests>=2.21.0', 'collection-json>=0.1.1', 'pudb', 'pfstate', 'pfmisc', 'webob'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['bin/chrisclient', 'bin/chrispl-run', 'bin/chrispl-search'],
      license          =   'MIT',
      zip_safe=False
)