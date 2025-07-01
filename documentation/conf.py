# vim: set filetype=python fileencoding=utf-8:
# -*- mode: python ; coding: utf-8 -*-

''' Configuration file for the Sphinx documentation builder.

    This file only contains a selection of the most common options.
    For a full list, see the documentation:
        https://www.sphinx-doc.org/en/master/usage/configuration.html
    Also, see this nice article on Sphinx customization:
        https://jareddillard.com/blog/common-ways-to-customize-sphinx-themes.html
'''


def _calculate_copyright_notice( ):
    from datetime import datetime as DateTime, timezone as TimeZone
    first_year = 2025
    now_year = DateTime.now( TimeZone.utc ).year
    if first_year < now_year: year_range = f"{first_year}-{now_year}"
    else: year_range = str( first_year )
    return f"{year_range}, Eric McDonald"


def _import_version( ):
    from importlib import import_module
    from pathlib import Path
    from sys import path
    project_location = Path( __file__ ).parent.parent
    path.insert( 0, str( project_location / 'sources' ) )
    module = import_module( 'ictruck' )
    return module.__version__


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'python-icecream-truck'
author = 'Eric McDonald'
copyright = ( # noqa: A001
    _calculate_copyright_notice( ) )
release = version = _import_version( )

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx_copybutton',
    'sphinx_inline_tabs',
]

templates_path = [ '_templates' ]

exclude_patterns = [ ]

rst_prolog = f'''
.. |project| replace:: {project}
'''

nitpicky = True
nitpick_ignore = [
    # Workaround for https://bugs.python.org/issue11975
    # Found on Stack Overflow (credit to Astropy project):
    #   https://stackoverflow.com/a/30624034
    ( 'py:class', "D[k] if k in D, else d.  d defaults to None." ),
    ( 'py:class', "None.  Remove all items from D." ),
    ( 'py:class', "a set-like object providing a view on D's items" ),
    ( 'py:class', "a set-like object providing a view on D's keys" ),
    ( 'py:class', "an object providing a view on D's values" ),
    ( 'py:class', "functools.partial" ),
    ( 'py:class', "mappingproxy" ),
    ( 'py:class', "module" ),
    ( 'py:class',
      "v, remove specified key and return the corresponding value." ),
    # Type annotation weirdnesses.
    ( 'py:class', "_thread.allocate_lock" ),
    ( 'py:class', "Doc" ),
    ( 'py:class', "absence.objects.AbsentSingleton" ),
    ( 'py:class', "accretive.__.imports.Annotated" ),
    ( 'py:class', "accretive.__.imports.H" ),
    ( 'py:class', "accretive.__.imports.V" ),
    ( 'py:class', "accretive.dictionaries.Annotated" ),
    ( 'py:class', "accretive.dictionaries.Dictionary" ),
    ( 'py:class', "builtins.NotImplementedType" ),
    ( 'py:class', "builtins.traceback" ),
    ( 'py:class', "collections.abc.Annotated" ),
    ( 'py:class', "frigid.classes.DataclassObject" ),
    ( 'py:class', "frigid.classes.Object" ),
    ( 'py:class', "frigid.dictionaries.Annotated" ),
    ( 'py:class', "frigid.dictionaries.Dictionary" ),
    ( 'py:class', "icecream.icecream.IceCreamDebugger" ),
    ( 'py:class', "ictruck.__.nomina.H" ),
    ( 'py:class', "ictruck.__.nomina.V" ),
    ( 'py:class', "ictruck.configuration.Annotated" ),
    ( 'py:class', "ictruck.recipes.rich.Annotated" ),
    ( 'py:class', "ictruck.recipes.sundae.Annotated" ),
    ( 'py:class', "ictruck.vehicles.Annotated" ),
    ( 'py:class', "rich.console.Console" ),
    ( 'py:class', "rich.style.Style" ),
    ( 'py:class', "types.Annotated" ),
    ( 'py:class', "typing_extensions.Any" ),
    ( 'py:class', "typing_extensions.Self" ),
    ( 'py:class', "typing_extensions.TypeIs" ),
    ( 'py:func', "__.register_module" ),
]

# -- Options for linkcheck builder -------------------------------------------

linkcheck_ignore = [
    # Circular dependency between building HTML and publishing it.
    r'https://emcd\.github\.io/python-icecream-truck/.*',
    # Stack Overflow rate limits too aggressively, which breaks matrix builds.
    r'https://stackoverflow\.com/help/.*',
    # Repository does not exist during initial development.
    r'https://github\.com/emcd/python-icecream-truck',
    r'https://github\.com/emcd/python-icecream-truck/.*',
    # Package does not exist during initial development.
    r'https://pypi.org/project/ictruck/',
    # Github aggressively rate-limits access to certain blobs.
    r'https://github\.com/.*/.*/blob/.*',
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.
# https://github.com/pradyunsg/furo
html_theme = 'furo'
html_theme_options = {
    'navigation_with_keys': True,
    'sidebar_hide_name': True,
}

html_static_path = [ '_static' ]

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    'member-order': 'groupwise',
    'members': True,
    'show-inheritance': True,
    # 'special-members': '__call__',
}

autodoc_typehints = 'none'
autodoc_use_type_comments = False

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': (
        'https://docs.python.org/3', None),
    'typing-extensions': (
        'https://typing-extensions.readthedocs.io/en/latest', None),
}

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
