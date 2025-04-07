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

:tocdepth: 4


*******************************************************************************
API
*******************************************************************************


Package ``ictruck``
===============================================================================

A debugging library that enhances the `icecream
<https://github.com/gruns/icecream>`_ package with flexible, flavorful traces
and module-specific configurations. Designed for both application and library
developers, it provides granular control over debug output while ensuring
isolation between different configurations.

* ``Truck``: Core class managing debugger instances with support for trace
  levels, custom flavors, and configurable output sinks.

* ``install``: Installs a configured ``Truck`` instance into Python builtins
  for universal access.

* ``register_module``: Registers module-specific configurations, ideal for
  libraries to define their own debugging behavior without affecting others.

* ``ModuleConfiguration``: Defines per-module settings, including prefixes,
  flavors, and formatters, with inheritance from a global configuration.

* Assorted recipes for extending the core functionality of the package.

The package organizes its functionality across several modules, providing
exceptions, configuration hierarchies, and specialized output recipes.


Module ``ictruck.vehicles``
-------------------------------------------------------------------------------

.. automodule:: ictruck.vehicles


Module ``ictruck.configuration``
-------------------------------------------------------------------------------

.. automodule:: ictruck.configuration


Module ``ictruck.printers``
-------------------------------------------------------------------------------

.. automodule:: ictruck.printers


Module ``ictruck.recipes.logging``
-------------------------------------------------------------------------------

.. automodule:: ictruck.recipes.logging


Module ``ictruck.recipes.rich``
-------------------------------------------------------------------------------

.. automodule:: ictruck.recipes.rich


Module ``ictruck.recipes.sundae``
-------------------------------------------------------------------------------

.. automodule:: ictruck.recipes.sundae


Module ``ictruck.exceptions``
-------------------------------------------------------------------------------

.. automodule:: ictruck.exceptions
