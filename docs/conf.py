import sys
import os
import re


sys.path.insert(0, os.path.join(os.getcwd(), '..', 'topgg'))
sys.path.insert(0, os.path.abspath('..'))

from version import VERSION


project = 'topggpy'
author = 'null8626'

copyright = ''
with open('../LICENSE', 'r') as f:
  copyright = re.search(r'[\d\-]+ null8626', f.read()).group()

version = VERSION
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx_reredirects']

intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
}

redirects = {
  'support-server': 'https://discord.gg/dbl',
  'repository': 'https://github.com/top-gg-community/python-sdk',
  'raw-api-reference': 'https://docs.top.gg/docs/',
}

html_css_files = [
  'style.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Roboto+Mono&display=swap',
]
html_js_files = ['script.js']
html_static_path = ['_static']
html_theme = 'furo'
html_title = project
