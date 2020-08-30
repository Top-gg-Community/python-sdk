import os
import re

from setuptools import find_packages, setup


on_rtd = os.getenv('READTHEDOCS') == 'True'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

if on_rtd:
    requirements.append('sphinxcontrib-napoleon')

with open('dbl/__init__.py') as f:
    # version = re.search(r"__version__\s*=\s*((\"|\')(\w).+\2)", f.read())
    init_file = f.read()
    author = re.search(r"^__author__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", init_file, re.MULTILINE).group(1)
    version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", init_file, re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()

setup(name='dblpy',
      author='{author}, top.gg'.format(author=author),
      author_email='shivaco.osu@gmail.com',
      url='https://github.com/top-gg/DBL-Python-Library',
      version=version,
      packages=find_packages(),
      license='MIT',
      description='A simple API wrapper for top.gg written in Python.',
      long_description=readme,
      include_package_data=True,
      python_requires='>= 3.5.3',
      install_requires=requirements,
      keywords='discord bot list discordbots botlist topgg top.gg',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ]
      )
