import codecs
from setuptools import setup, find_packages
import os
import re
import sys


if sys.version_info < (3, 5, 3):
    raise RuntimeError("aiohttp 3.x requires Python 3.5.3+")


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_mako', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ['aiohttp>=3.0', 'mako>=1.0.0']


setup(name='aiohttp-mako',
      version=version,
      description=("mako template renderer for aiohttp.web "
                   "(http server for asyncio)"),
      lond_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Nikolay Novik',
      author_email='nickolainovik@gmail.com',
      url='https://github.com/aio-libs/aiohttp-mako/',
      license='Apache 2',
      packages=find_packages(),
      python_requires='>=3.5.3',
      install_requires=install_requires,
      include_package_data=True)
