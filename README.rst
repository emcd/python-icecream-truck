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
                                  icecream-truck
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/icecream-truck
   :alt: Package Version
   :target: https://pypi.org/project/icecream-truck/

.. image:: https://img.shields.io/pypi/status/icecream-truck
   :alt: PyPI - Status
   :target: https://pypi.org/project/icecream-truck/

.. image:: https://github.com/emcd/python-icecream-truck/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-icecream-truck/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-icecream-truck/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-icecream-truck/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-icecream-truck
   :alt: Project License
   :target: https://github.com/emcd/python-icecream-truck/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/icecream-truck
   :alt: Python Versions
   :target: https://pypi.org/project/icecream-truck/

.. image:: https://raw.githubusercontent.com/emcd/python-icecream-truck/master/data/pictures/logo.svg
   :alt: Icecream Truck Logo
   :width: 800
   :align: center


🍦 **Flavorful Debugging** - A Python library which enhances the powerful and
well-known `icecream <https://github.com/gruns/icecream>`_ package with
flavored traces, module hierarchies, and custom outputs. Load up the truck and
roll out delicious debug prints for applications and libraries alike!

Key Features ⭐
===============================================================================

🍒 **Debugger Flavors**: Numeric trace depths to control level of debugging
detail (e.g., ``1``) or custom named flavors for specific subsystems (e.g.,
``io``, ``reporting``), traditional logging levels (e.g., ``info``, ``error``),
or whatever else you can imagine.

🌳 **Module Hierarchy**: Global and per-module configs with inheritance for
precise control over output prefixes, formatters, custom flavors, etc....

🖨️ **Printer Factory**: Dyanamically associate output functions with debugger
objects based on module name, flavor, etc... — swap in customized ``print``,
``logging``, ``rich.console``, or other sinks as desired.

📚 **Library-Friendly**: Non-intrusive registration for libraries without
stepping on application debugger/logging configuration.

🚦 **Disabled by Default**: Can leave in production code and explicitly
activate portions as needed. (Performance and security considerations
notwithstanding.)

Installation 📦
===============================================================================

::

    pip install icecream-truck

Examples 💡
===============================================================================

Universal Availability
-------------------------------------------------------------------------------

Install as a Python builtin (default alias, ``ictr``) and then use anywhere in
your codebase:

.. code-block:: python

    from ictruck import install
    install( trace_levels = 3 )  # Enable TRACE0 to TRACE3
    message = "Hello, debug world!"
    ictr( 1 )( message )  # Prints: TRACE1| message: 'Hello, debug world!'

Library Registration
-------------------------------------------------------------------------------

Libraries can register their own configurations without overriding those of the
application or other libraries. By default, the name of the calling module is
used to register a configuration:

.. code-block:: python

    from ictruck import ModuleConfiguration, register_module
    register_module( configuration = ModuleConfiguration( ... ) )

Recipes for Customization
-------------------------------------------------------------------------------

E.g., integrate ``icecream``-based introspection and formatting with the
``logging`` module in the Python standard library:

.. code-block:: python

    import logging
    from ictruck import produce_logging_truck
    logging.basicConfig( level = logging.INFO )
    truck = produce_logging_truck( )
    admonition = "Careful now!"
    answer = 42
    truck( 'warning' )( admonition )  # Logs: WARNING:__main__:ic| admonition: 'Careful now!'
    truck( 'info' )( answer )         # Logs: INFO:__main__:ic| answer: 42
    ## Note: Module name will be from whatever module calls the truck.

Motivation 🚚
===============================================================================

Why ``icecream-truck``?

There is nothing wrong with the ``icecream`` or ``logging`` packages. However,
there are times that the author of ``icecream-truck`` has wanted, for various
reasons, more than these packages inherently offer:

* **Coexistence**: Application and libraries can coexist without configuration
  clashes.

  - Library developers are `strongly advised not to create custom levels
    <https://docs.python.org/3/howto/logging.html#custom-levels>`_ in
    ``logging``.

  - Library developers are `advised on how to avoid polluting stderr
    <https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library>`_
    in ``logging``, when an application has not supplied a configuration.

  - Loggers `propagate upwards
    <https://docs.python.org/3/library/logging.html#logging.Logger.propagate>`_
    by default in ``logging``. This means that libraries must explicitly
    opt-out of propagation if their authors want to be good citizens and not
    contribute to noise pollution / signal obfuscation.

* **Granularity**: Control of debug output by depth threshold and subsystem.

  - Only one default debugging level (``DEBUG``) with ``logging``. Libraries
    cannot safely extend this. (See point about coexistence).

  - No concept of debugging level with ``ic`` builtin. Need to orchestrate
    multiple ``icecream.IceCreamDebugger`` instances to support this. (In fact,
    this is what ``icecream-truck`` does.)

  - While logger hierarchies in ``logging`` do support the notion of software
    subsystems, hierarchies are not always the most convenient or abbreviated
    way of representing subsystems which span parts or entireties of modules.

* **Signal**: Prevention of undesirable library chatter.

  - The ``logging`` root logger will log all messages, at its current log
    level or higher, which propagate up to it. Many Python libraries have
    opt-out rather than opt-in logging, so you see all of their ``DEBUG`` and
    ``INFO`` spam unless you surgically manipulate their loggers or squelch
    the overall log level.

  - Use of the ``ic`` builtin is only recommended for temporary debugging. It
    cannot be left in production code without spamming. While the ``enabled``
    flag on the ``ic`` builtin can be set to false, it is easy to forget and
    also applies to every place where ``ic`` is used in the code. (See point
    about granularity.)

* **Extensibility**: More natural integration with packages like ``rich`` via
  robust recipes.

  - While it is not difficult to change the ``argToStringFunction`` on ``ic``
    to be ``rich.pretty.pretty_repr``, there is some repetitive code involved
    in each project which wants to do this. And, from a safety perspective,
    there should be a fallback if ``rich`` fails to import.

  - Similarly, one can add a ``rich.logging.RichHandler`` instance to a logger
    instance with minimal effort. However, depending on the the target output
    stream, one may also need to build a ``rich.console.Console`` first and
    pass that to the handler. This handler will also compete with whatever
    handler has been set on the root logger. So, some care must be taken to
    prevent propagation. Again, this is repetitive code across projects and
    there are import safety fallbacks to consider.

Contribution 🤝
===============================================================================

Contributions welcome! See the `contribution guide
<https://github.com/emcd/python-icecream-truck/tree/master/documentation/sphinx/contribution>`_
for details.

`More Flair <https://www.imdb.com/title/tt0151804/characters/nm0431918>`_
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-icecream-truck
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-icecream-truck

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
   :alt: Bandit
   :target: https://github.com/PyCQA/bandit

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :alt: Pylint
   :target: https://github.com/pylint-dev/pylint

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
   :alt: Hypothesis
   :target: https://hypothesis.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/implementation/icecream-truck
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/icecream-truck/

.. image:: https://img.shields.io/pypi/wheel/icecream-truck
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/icecream-truck/
