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

The ``recipes`` module provides pre-configured ``Truck`` instances integrated
with Python’s ``logging`` module, using standard logging flavors.

Logging Integration
-------------------------------------------------------------------------------

Start with ``produce_logging_truck`` for logging with predefined flavors
(``debug``, ``info``, ``warning``, ``error``, ``critical``):

.. code-block:: python

    import logging
    from ictruck.recipes import produce_logging_truck
    logging.basicConfig( level = logging.INFO )
    produce_logging_truck( )  # Installs as ictr
    task_id = 42
    ictr( 'info' )( task_id )
    # Output: INFO:__main__:task_id: 42
    value = 0
    ictr( 'warning' )( value )
    # Output: WARNING:__main__:value: 0
    ictr( 'debug' )( value )  # No output; below logging.INFO

Flavors map directly to `logging` levels—set ``install = False`` for a local
instance.

Flavor-to-Builtins Mapping
-------------------------------------------------------------------------------

Map logging flavors to shorthand names:

.. code-block:: python

    from ictruck.recipes import produce_logging_truck
    import builtins
    truck = produce_logging_truck( install = False )
    flavors = { 'debug': 'icd', 'info': 'ici', 'warning': 'icw' }
    for flavor, name in flavors.items( ):
        setattr( builtins, name, truck( flavor ) )
    step = 1
    icd( step )
    # Output: DEBUG:__main__:step: 1
    status = 'OK'
    ici( status )
    # Output: INFO:__main__:status: 'OK'

This provides concise aliases for logging-based debugging.
