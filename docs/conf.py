# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'


master_doc = 'index'

# General information about the project.
project = u'wellbehaved'
project_id = u'wellbehaved'
company = 'BARS Group'
copyright = u'2013-%s, %s' % (datetime.now().year, company)

version = '0.1.2.0'
release = '0.1.2.0'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'

html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'wellbehaveddoc'

autodoc_default_flags = ['members', 'undoc-members']
