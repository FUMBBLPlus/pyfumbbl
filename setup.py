"""
pyfumbbl setup module.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import re


here = path.abspath(path.dirname(__file__))

with open(
    path.join(here, 'README.md'),
    encoding='utf-8'
) as f:
  readme = f.read()

version_file_path = path.join(
    path.dirname(__file__),
    'pyfumbbl',
    '__init__.py',
)
with open(version_file_path, encoding='utf8') as f:
  metadata = dict(
      re.findall(r'__([a-z]+)__ = \'([^\']+)',
      f.read())
  )

setup(
  name='pyfumbbl',
  version=metadata['version'],
  description='FUMBBL Python Library',
  long_description=readme,
  url='https://bitbucket.org/SzieberthAdam/pyfumbbl',
  author='Szieberth Ádám',
  author_email='sziebadam@gmail.com',
  license='MIT',
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Games/Entertainment :: Board Games'
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3 :: Only',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      ],
  keywords=['game', 'fantasyfootball', 'fumbbl',],
  packages=find_packages(exclude=['test*']),
  package_dir={'pyfumbbl': './pyfumbbl'},
  include_package_data=True,
  install_requires=[
      'requests',
      'yarl',
      ],
  extras_require={
      #'docs': ['sphinx'],
      },
  scripts=[
      ]
  )
