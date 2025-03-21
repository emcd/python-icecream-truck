

.. towncrier release notes start

Ictruck 1.0 (2025-03-21)
========================

Features
--------

- Add ability to install truck as a Python builtin for global availability throughout a codebase.
- Add customizable prefix emitters and formatters per flavor for fine-grained control over debug output appearance.
- Add hierarchical configuration system with inheritance for precise control over debug output across different modules and packages.
- Add non-intrusive registration system allowing libraries to configure debugging without interfering with application settings.
- Add numeric trace depth flavors (0-9) and support for custom named flavors (e.g., 'info', 'auth', 'database') for targeted debugging output.
- Add printer factory system to dynamically route debug output to different destinations based on module name, flavor, or other criteria.
- Add recipe for integration with the Rich library, providing colorful and formatted debug output in terminal environments.
- Add recipe for seamless integration with Python's standard logging module, mapping flavors to logging levels.
- Add safe-for-production capability with disabled-by-default trace levels and flavors that can be selectively activated when needed.


Supported Platforms
-------------------

- Add support for CPython 3.10 through 3.13.
