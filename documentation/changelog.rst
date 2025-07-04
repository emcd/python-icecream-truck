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


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

Ictruck 1.5 (2025-07-04)
========================

Enhancements
------------

- Prepare for deprecation of ``from __future__ import annotations``.
- Use ``frigid.finalize_module`` instead of separate Dynadoc and Frigid calls to
  finalize module. Simplifies finialization and avoids a deprecation warning.


Ictruck 1.4 (2025-07-01)
========================

Enhancements
------------

- Apply Dynadoc to extract documentation annotations from class and function
  signatures.


Ictruck 1.3 (2025-06-05)
========================

Enhancements
------------

- Internals update - nothing to see here. Lock versions of some dependencies in
  anticipation of breaking changes.


Ictruck 1.2 (2025-04-06)
========================

Features
--------

- Default printer factory available in public API. Enhanced to strip ANSI C1
  sequences (including colors and other character cell attributes) if output
  stream is not attached to a TTY. Improved support for legacy Windows consoles.
- New recipe: Sundae. Supports emoji and colorization of prefixes and
  colorization of formatted values (via Rich). Trace depths follow a color
  gradient. Custom flavors: ``note``, ``monition``, ``error``, ``abort``,
  ``errorx`` (error with exception traceback), ``abort`` (abort with exception
  traceback), ``success``, and ``future``.
- Support configuration of icecream trucks via environment variables. By default,
  the names are ``ICTRUCK_ACTIVE_FLAVORS`` and ``ICTRUCK_TRACE_LEVELS``, but
  these are configurable during the production or installation of a truck.


Ictruck 1.1 (2025-03-30)
========================

Features
--------

- Use of ``install`` now preserves previously registered module configurations on
  new icecream truck being installed into the Python builtins. This allows
  libraries to register module configurations before applications install an
  icecream truck, thus providing greater flexibility around initialization-time
  and runtime sequencing of operations.

  Note that this is a mildly breaking change in the sense that installation would
  refuse to proceed if a matching name already existed in the ``builtins``
  module.


Ictruck 1.0 (2025-03-21)
========================

Features
--------

- Add ability to install truck as a Python builtin for global availability
  throughout a codebase.
- Add customizable prefix emitters and formatters per flavor for fine-grained
  control over debug output appearance.
- Add hierarchical configuration system with inheritance for precise control
  over debug output across different modules and packages.
- Add non-intrusive registration system allowing libraries to configure
  debugging without interfering with application settings.
- Add numeric trace depth flavors (0-9) and support for custom named flavors
  (e.g., 'info', 'auth', 'database') for targeted debugging output.
- Add printer factory system to dynamically route debug output to different
  destinations based on module name, flavor, or other criteria.
- Add recipe for integration with the Rich library, providing colorful and
  formatted debug output in terminal environments.
- Add recipe for seamless integration with Python's standard logging module,
  mapping flavors to logging levels.
- Add safe-for-production capability with disabled-by-default trace levels and
  flavors that can be selectively activated when needed.


Supported Platforms
-------------------

- Add support for CPython 3.10 through 3.13.
