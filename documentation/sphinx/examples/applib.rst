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


Library Coordination
===============================================================================

Application and Module with Custom Flavors
-------------------------------------------------------------------------------

(Example courtesy of Anthropic claude-3-7-sonnet.)

An example application which uses a library module for some analytics:

.. literalinclude:: ../../../examples/applib/__main__.py
   :language: python

And the library module for analytics:

.. literalinclude:: ../../../examples/applib/analytics.py
   :language: python

Running this will result in::

    TRACE0| 'Application running.'
    TRACE0| 'Calculating metrics...'
    ANALYTICS INFO| 'Calculating metrics...'
    ANALYTICS INFO| 'Metrics calculation complete.'
    ANALYTICS PERF| count: 10
    TRACE1| metrics: {'average': 11.6,
                      'count': 10,
                      'maximum': 14,
                      'minimum': 10,
                      'std_dev': 1.3564659966250536,
                      'total': 116,
                      'variance': 1.8399999999999999}
    TRACE0| 'Detecting anomalies...'
    ANALYTICS INFO| f"Detecting anomalies with threshold {threshold}.": 'Detecting anomalies with threshold 2.0.'
    ANALYTICS INFO| 'Calculating metrics...'
    ANALYTICS INFO| 'Metrics calculation complete.'
    ANALYTICS PERF| count: 10
    ANALYTICS PERF| len( anomalies ): 1
    TRACE1| summary: 'Found 1 anomalies.'
    TRACE2| position: 5, value: 40, z_score: 2.975954728492207
    TRACE0| 'Calculating metrics on empty dataset...'
    ANALYTICS INFO| 'Calculating metrics...'
    ANALYTICS ERROR| 'Empty dataset provided.'
    TRACE0| 'Application finished'
