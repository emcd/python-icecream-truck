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


Simple Cases
===============================================================================

Adjustable Trace Level via Environment Variable
-------------------------------------------------------------------------------

By default, ``icecream-truck`` does not produce any output. You, as an
application developer, will need to determine how much output you want from it
and whether you will let your users adjust that knob. Having a default trace
depth, which can be overridden by environment variable is one simple way to
achieve this.

.. literalinclude:: ../../../examples/simple/trucker.py
   :language: python

Running this will result in::

    TRACE0| 'Icecream tracing active.'
    TRACE2| operator: <built-in function mul>
    TRACE1| answer: 42

Running this with ``ICTRUCK_TRACE_LEVELS=3`` in the environment will result
in::

    TRACE0| 'Icecream tracing active.'
    TRACE2| operator: <built-in function mul>
    TRACE3| datum: 2
    TRACE3| datum: 3
    TRACE3| datum: 7
    TRACE1| answer: 42
