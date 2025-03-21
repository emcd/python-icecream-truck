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

Running the Examples
====================

The directories under this directory contain example code demonstrating the
features of the ``ictruck`` package. To run these examples, ensure that
``ictruck`` is installed in the Python environment used by your interpreter.
Below are the recommended methods to execute the examples.

Prerequisites
-------------

The ``icecream-truck`` package distribution must be installed in your Python
environment. We recommend using a virtual environment to isolate dependencies:

- Create and activate a virtual environment:
  ::

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

- Install ``ictruck``:
  ::

      pip install icecream-truck

Alternatively, if you have `Hatch <https://github.com/pypa/hatch>`_ installed,
you can use it to manage the environment and run the examples directly (see
below).

Method 1: Using ``python -m`` from Project Root
----------------------------------------------

From the top-level directory of the ``icecream-truck`` project (where
``pyproject.toml`` resides), run the example as a module:

::

    python -m examples.<directory_name>

Replace ``<directory_name>`` with the name of the relevant example directory
(e.g., ``applib``, ``logging``). This method ensures the module search path
includes the project structure correctly.

Method 2: Running the Script Directly
-------------------------------------

From within an example directory, run the driver script directly:

::

    python __main__.py

Ensure your current working directory is that directory, or provide the full
path to ``__main__.py`` if running from elsewhere (e.g., ``python
examples/<directory_name>/__main__.py`` from the project root).

Using Hatch
-----------

If Hatch is installed, you can run the examples without manually managing a
virtual environment:

::

    hatch run python -m examples.<directory_name>

Or, for the script method:

::

    hatch run python __main__.py

This leverages Hatch’s built-in environment management to ensure dependencies
are satisfied.

Notes
-----

- Some examples may rely on environment variables (e.g., ``TRACE_LEVELS``) to
  control debugging output. Check the source code or accompanying documentation
  for details.
- For consistent results, use a virtual environment or Hatch to avoid
  conflicts with other installed packages.
- Some examples may use additional third-party packages, such as ``rich``. To
  ensure that you have these dependencies installed, ``hatch --env develop run
  python -m examples.<directory_name>`` can be used.
