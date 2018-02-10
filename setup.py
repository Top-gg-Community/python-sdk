import re
import sys
import os

from setuptools import setup, find_packages


on_rtd = os.getenv('READTHEDOCS') == 'True'

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

if on_rtd:
    requirements.append('sphinxcontrib-napoleon')

with open('dbl/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()

setup(name='dblpy',
      author='Francis Taylor, discordbots.org',
      author_email='contact@franc.ist',
      url='https://github.com/DiscordBotList/DBL-Python-Library ',
      version=version,
      packages=find_packages(),
      license='MIT',
      description='A simple API wrapper for discordbots.org written in Python',
      long_description=readme,
      include_package_data=True,
      python_requires='>= 3.5',
      install_requires=requirements,
      keywords='discord bot list discordbots botlist',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ]
      )
