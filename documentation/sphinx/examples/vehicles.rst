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


Vehicles
===============================================================================

The ``vehicles`` module provides the ``Truck`` class and utilities for
debugging with global or module-specific configurations. These examples
showcase variable name inference with numeric trace levels and custom flavors.

Installing into Builtins
-------------------------------------------------------------------------------

Install a ``Truck`` as ``ictr`` with numeric trace levels for instant variable
debugging:

.. code-block:: python

    from ictruck.vehicles import install
    install( trace_levels = 2 )  # Enables TRACE0 to TRACE2
    message = "Hello, debug world!"
    ictr( 1 )( message )
    # Output: TRACE1| message: 'Hello, debug world!'
    x = 42
    ictr( 0 )( x, message )
    # Output: TRACE0| x: 42, message: 'Hello, debug world!'
    ictr( 3 )( x )  # No output; exceeds trace level 2

This mirrors ``icecream``’s ``ic``—variable names are inferred automatically,
controlled by ``trace_levels`` (0-9) with default ``TRACE{i}|`` prefixes.

Add custom flavors for subsystem-specific debugging:

.. code-block:: python

    from ictruck import VehicleConfiguration, FlavorConfiguration
    flavors = {
        'io': FlavorConfiguration( prefix = 'IO: ' ),
        'calc': FlavorConfiguration( prefix = 'CALC: ' )
    }
    config = VehicleConfiguration( flavors = flavors )
    install( generalcfg = config, active_flavors = { 'io', 'calc' } )
    path = '/tmp/data'
    ictr( 'io' )( path )
    # Output: IO: path: '/tmp/data'
    result = 15
    ictr( 'calc' )( result )
    # Output: CALC: result: 15

This is perfect for applications needing a global, tailored debugger.

Module-Specific Configuration
-------------------------------------------------------------------------------

Library developers can isolate debug output with ``register_module``:

.. code-block:: python

    # In mylib.py
    from ictruck import Truck, ModuleConfiguration
    truck = Truck( trace_levels = 1 )  # TRACE0 and TRACE1
    config = ModuleConfiguration( prefix = 'LIB: ' )
    truck.register_module( 'mylib', configuration = config )
    state = 'ready'
    truck( 0 )( state )  # Module name inferred as 'mylib'
    # Output: LIB: state: 'ready'
    truck( 2 )( state )  # Above trace level, no output
    # In app code
    status = 'OK'
    truck( 1 )( status )  # Outside mylib, uses default config
    # Output: TRACE1| status: 'OK'

This keeps library debugging separate, with variable inference intact, avoiding
global namespace conflicts.

Direct Truck Usage
-------------------------------------------------------------------------------

For local debugging without ``builtins``:

.. code-block:: python

    # In some_module.py
    from ictruck import Truck
    truck = Truck( trace_levels = 1 )  # TRACE0 and TRACE1
    count = 5
    truck( 0 )( count )
    # Output: TRACE0| count: 5
    truck( 2 )( count )  # Above trace level, no output

Use this for temporary debugging, leveraging variable name inference locally.
Note: Module name inference assumes a real module context (e.g., a `.py` file).
