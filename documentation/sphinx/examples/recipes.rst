.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


Recipes
===============================================================================

The ``recipes`` package provides convenience modules for various tasks like
integration with Python standard library logging or use of the ``rich`` package
for formatting or printing.

Logging Integration
-------------------------------------------------------------------------------

(Example courtesy of xAI grok-3.)

.. literalinclude:: ../../../examples/logging/__main__.py
   :language: python


Running this will result in the following::

    INFO: ic| 'Scanning', files: ['data1.txt', 'data2.txt']
    WARNING: ic| 'Missing', file: 'data1.txt'
    WARNING: ic| 'Missing', file: 'data2.txt'


``rich`` Integration
-------------------------------------------------------------------------------

(Example courtesy of xAI grok-3.)

.. literalinclude:: ../../../examples/rich/__main__.py
   :language: python

Running this will result in the following (or something similar, depending on
your terminal colors and width):

.. image:: recipe-rich-termcap.png
   :alt: Rich Recipe Terminal Screen Capture
   :width: 800
   :align: center
