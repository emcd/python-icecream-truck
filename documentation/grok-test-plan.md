# Testing Strategy for `icecream-truck`

## Overview

This document outlines the testing strategy for the `icecream-truck` Python package, a debugging enhancement over the `icecream` library. The strategy ensures comprehensive coverage of functionality, configuration isolation, thread safety, and adherence to the project’s coding practices.

### Goals
- **Unit Tests**: Verify individual components (`Truck`, `install`, `register_module`, `exceptions`, etc.).
- **Integration Tests**: Test configuration hierarchy, flavor handling, and trace levels.
- **Isolation Tests**: Ensure library configurations don’t interfere with application or other libraries.
- **Thread Safety**: Validate concurrent access to shared resources (e.g., `_debuggers` cache).
- **Coverage**: Maintain or improve code coverage (already configured with `pytest-cov`).

### Tools
- **pytest**: For test execution and fixtures.
- **pyfakefs**: For filesystem simulation in isolation tests.
- **hypothesis**: For property-based testing.
- **unittest.mock**: For mocking where necessary (minimal due to dependency injection).
- **io.StringIO**: For simple output capture.
- **logging**: For structured log capture.

### Test Modules
Tests will be organized under `tests/test_000_ictruck/` with the following modules:
- `test_100_exceptions.py`: Tests for the `exceptions` module.
- `test_200_configuration.py`: Tests for the `configuration` module (prefix inheritance, configuration merging).
- `test_300_vehicles.py`: Tests for the `vehicles` module (core functionality, recipes, thread safety, isolation).

## Project Coding Practices and Style

### Coding Style (from `documentation/sphinx/development/style.rst`)
- **Spacing**: Use spaces around operators, delimiters, and in function definitions (e.g., `def func( arg = 42 )`).
- **Line Width**: Maximum 79 columns.
- **Vertical Compactness**: Single-line bodies for simple functions, no blank lines within function bodies, functions under 30 lines.
- **Docstrings**: Triple single quotes, one space after opening/before closing for single-line, newlines for multi-line.
- **Imports**: Prefer function-level imports to avoid namespace pollution, use parentheses for multi-line imports.
- **Collections**: Trailing comma for multi-line collections, single space in empty literals.
- **Single-Line Statements**: Use for simple control flow (e.g., `if not data: return None`).

### Practices (from `documentation/sphinx/development/practices.rst`)
- **Documentation**: Use Sphinx reStructuredText, no parameter/return type docs in docstrings (handled by PEP 727 annotations).
- **Exceptions**: Raise package-specific exceptions for failures, never swallow exceptions.
- **Imports**: Use function-level imports or common imports in `__` package base.
- **Quality Assurance**: Maintain high code coverage, consider untested edge cases.

### Test Conventions (from `tests/test_000_ictruck/`)
- **Module Structure**: Tests are in `tests/test_000_ictruck/`, with files named `test_<number>_<module>.py` (e.g., `test_000_package.py`).
- **Imports**: Use `cache_import_module` from the test package for importing modules under test (e.g., `cache_import_module( 'ictruck' )`).
- **Test Naming**: Functions named `test_<number>_<description>` (e.g., `test_000_sanity`), with numbers indicating order/priority.
- **Docstrings**: Single-line docstrings with a space after/before quotes (e.g., `''' Test description. '''`).
- **Parameterization**: Use `pytest.mark.parametrize` with tuples for test data (e.g., `('value',)`).

## Fixtures

Fixtures will be defined in `tests/test_000_ictruck/__init__.py` to be shared across test modules.

```python
# tests/test_000_ictruck/__init__.py (extended)

# Existing imports and utilities...

import io
import logging
import sys
from importlib import import_module

def setup_truck( config ):
    ''' Sets up a Truck instance with a simple output capture. '''
    output = io.StringIO( )
    printer = lambda mname, flavor: lambda x: output.write( x + '\n' )
    from ictruck.vehicles import Truck
    return Truck( printer_factory = printer, **config ), output

def setup_structured_truck( config ):
    ''' Sets up a Truck instance with a structured output capture. '''
    class OutputCapture:
        def __init__( self ):
            self.outputs = [ ]
            self.buffer = io.StringIO( )
        def printer( self, mname, flavor ):
            def printer( text ):
                self.outputs.append( ( mname, flavor, text ) )
                self.buffer.write( f"{mname}:{flavor}:{text}\n" )
            return printer
        def __del__( self ):
            self.buffer.close( )
    capture = OutputCapture( )
    from ictruck.vehicles import Truck
    return Truck( printer_factory = capture.printer, **config ), capture

def setup_logging_capture( ):
    ''' Sets up a hybrid logging capture. '''
    class LogCapture( logging.Handler ):
        def __init__( self ):
            super( ).__init__( )
            self.records = [ ]
            self.output = io.StringIO( )
        def emit( self, record ):
            self.records.append( record )
            self.output.write( f"{record.levelname}:{record.module}:{record.msg}\n" )
        def __del__( self ):
            self.output.close( )
    capture = LogCapture( )
    logger = logging.getLogger( )
    original_level = logger.level
    logger.setLevel( logging.DEBUG )
    logger.addHandler( capture )
    return capture, logger, original_level

def cleanup_logging_capture( capture, logger, original_level ):
    ''' Cleans up a logging capture setup. '''
    logger.removeHandler( capture )
    logger.setLevel( original_level )

def setup_filesystem( fs, module_name, content ):
    ''' Sets up a fake filesystem with a module. '''
    fs.create_file(
        f"{module_name}/__init__.py",
        contents = content )

def setup_builtins_isolation( ):
    ''' Isolates builtins for testing. '''
    import builtins
    original = builtins.__dict__.copy( )
    return original

def cleanup_builtins_isolation( original ):
    ''' Restores builtins after testing. '''
    import builtins
    builtins.__dict__.clear( )
    builtins.__dict__.update( original )
```

## Test Modules

### `test_100_exceptions.py`

This module tests the `exceptions` module, ensuring custom exceptions are raised correctly and adhere to project practices (e.g., proper exception chaining).

```python
# tests/test_000_ictruck/test_100_exceptions.py

# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#

''' Tests for the exceptions module. '''

import pytest

from . import cache_import_module, setup_builtins_isolation, cleanup_builtins_isolation

@pytest.fixture
def exceptions( ):
    ''' Provides the exceptions module. '''
    yield cache_import_module( 'ictruck.exceptions' )

def test_000_argument_class_invalidity( exceptions ):
    ''' Exception for invalid argument class is raised correctly. '''
    with pytest.raises( exceptions.ArgumentClassInvalidity ) as exc_info:
        raise exceptions.ArgumentClassInvalidity( 'arg', int )
    assert str( exc_info.value ) == "Argument 'arg' must be an instance of builtins.int."

def test_010_flavor_inavailability( exceptions ):
    ''' Exception for unavailable flavor is raised correctly. '''
    with pytest.raises( exceptions.FlavorInavailability ) as exc_info:
        raise exceptions.FlavorInavailability( 'debug' )
    assert str( exc_info.value ) == "Flavor 'debug' is not available."

def test_020_module_inference_failure( exceptions ):
    ''' Exception for module inference failure is raised correctly. '''
    with pytest.raises( exceptions.ModuleInferenceFailure ) as exc_info:
        raise exceptions.ModuleInferenceFailure( )
    assert str( exc_info.value ) == "Could not infer invoking module from call stack."

def test_030_omniexception_attributes( exceptions ):
    ''' Omniexception exposes only specified attributes. '''
    exc = exceptions.Omniexception( )
    visible_attrs = set( dir( exc ) )
    assert visible_attrs.issuperset( { '__cause__', '__context__' } )
    assert not visible_attrs.issuperset( { '_internal' } )  # Assuming no internal attrs exposed
```

### `test_200_configuration.py`

This module tests the `configuration` module, focusing on prefix inheritance, configuration merging, and module hierarchy.

```python
# tests/test_000_ictruck/test_200_configuration.py

# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#

''' Tests for the configuration module. '''

import pytest
from hypothesis import given, strategies as st

from . import cache_import_module, setup_truck

@pytest.fixture
def configuration( ):
    ''' Provides the configuration module. '''
    yield cache_import_module( 'ictruck.configuration' )

@pytest.fixture
def truck( request ):
    ''' Provides a Truck instance with configuration. '''
    config = getattr( request, 'param', { } )
    truck, output = setup_truck( config )
    yield truck, output
    output.close( )

@pytest.mark.parametrize(
    'config, expected_prefix',
    [
        ( { 'generalcfg': configuration.Vehicle( prefix = 'Vehicle| ' ) }, 'Vehicle| TRACE0| ' ),
        ( {
            'generalcfg': configuration.Vehicle( prefix = 'Vehicle| ' ),
            'modulecfgs': { 'test': configuration.Module( prefix = 'Module| ' ) }
        }, 'Module| TRACE0| ' ),
        ( {
            'generalcfg': configuration.Vehicle(
                prefix = 'Vehicle| ',
                flavors = { 0: configuration.Flavor( prefix = 'Flavor| ' ) }
            )
        }, 'Flavor| ' ),
        ( {
            'generalcfg': configuration.Vehicle( prefix = 'Vehicle| ' ),
            'modulecfgs': {
                'test': configuration.Module(
                    prefix = 'Module| ',
                    flavors = { 0: configuration.Flavor( prefix = 'Flavor| ' ) }
                )
            }
        }, 'Flavor| ' ),
    ],
    indirect = [ 'truck' ]
)
def test_000_prefix_inheritance( truck, expected_prefix, configuration ):
    ''' Prefix inheritance works as expected. '''
    truck_instance, _ = truck
    debugger = truck_instance( 0 )  # Mock module as "test" if needed
    assert debugger.prefix == expected_prefix

@given(
    vehicle_prefix = st.text( ),
    module_prefix = st.one_of( st.none( ), st.text( ) ),
    flavor_prefix = st.one_of( st.none( ), st.text( ) )
)
def test_100_configuration_merging( vehicle_prefix, module_prefix, flavor_prefix, configuration ):
    ''' Configuration merging follows precedence rules. '''
    vehicle_config = configuration.Vehicle( prefix = vehicle_prefix )
    module_config = configuration.Module( prefix = module_prefix )
    flavor_config = configuration.Flavor( prefix = flavor_prefix )
    config = { 'generalcfg': vehicle_config }
    if module_prefix is not None: config[ 'modulecfgs' ] = { 'test': module_config }
    if flavor_prefix is not None:
        flavors = config.get( 'generalcfg', vehicle_config ).flavors
        flavors[ 0 ] = flavor_config
    truck, output = setup_truck( config )
    try:
        debugger = truck( 0 )  # Mock module as "test" if needed
        expected = flavor_prefix if flavor_prefix is not None else (
            module_prefix + 'TRACE0| ' if module_prefix is not None else vehicle_prefix + 'TRACE0| ' )
        assert debugger.prefix == expected
    finally:
        output.close( )

@given(
    module_name = st.from_regex( r'[a-z]+(\.[a-z]+)*' ),
    parent_configs = st.dictionaries(
        keys = st.from_regex( r'[a-z]+(\.[a-z]+)*' ),
        values = st.builds(
            lambda p: configuration.Module( prefix = p ),
            st.text( ) )
    )
)
def test_200_module_hierarchy( module_name, parent_configs, configuration ):
    ''' Module hierarchy inheritance works correctly. '''
    truck, output = setup_truck( { 'modulecfgs': parent_configs } )
    try:
        from ictruck.vehicles import _iterate_module_name_ancestry
        debugger = truck( 0 )  # Mock module_name in _discover_invoker_module_name if needed
        expected_prefix = None
        for parent in _iterate_module_name_ancestry( module_name ):
            if parent in parent_configs:
                expected_prefix = parent_configs[ parent ].prefix + 'TRACE0| '
        if expected_prefix is None: expected_prefix = 'TRACE0| '  # Default from flavor
        assert debugger.prefix == expected_prefix
    finally:
        output.close( )
```

### `test_300_vehicles.py`

This module tests the `vehicles` module, including core functionality, recipes, thread safety, and isolation.

```python
# tests/test_000_ictruck/test_300_vehicles.py

# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#

''' Tests for the vehicles module. '''

import pytest
import random
import threading
from hypothesis import given, strategies as st

from . import (
    cache_import_module,
    setup_builtins_isolation, cleanup_builtins_isolation,
    setup_logging_capture, cleanup_logging_capture,
    setup_truck, setup_structured_truck, setup_filesystem
)

@pytest.fixture
def vehicles( ):
    ''' Provides the vehicles module. '''
    yield cache_import_module( 'ictruck.vehicles' )

@pytest.fixture
def truck( request ):
    ''' Provides a Truck instance with simple output capture. '''
    config = getattr( request, 'param', { } )
    truck, output = setup_truck( config )
    yield truck, output
    output.close( )

@pytest.fixture
def structured_truck( ):
    ''' Provides a Truck instance with structured output capture. '''
    truck, capture = setup_structured_truck( { } )
    yield truck, capture

@pytest.fixture
def log_capture( ):
    ''' Provides a hybrid logging capture. '''
    capture, logger, original_level = setup_logging_capture( )
    yield capture
    cleanup_logging_capture( capture, logger, original_level )

@pytest.fixture
def isolate_builtins( ):
    ''' Isolates builtins for testing. '''
    original = setup_builtins_isolation( )
    yield
    cleanup_builtins_isolation( original )

def test_000_install( vehicles, isolate_builtins ):
    ''' Installation adds Truck to builtins. '''
    truck = vehicles.install( alias = 'test_ictr' )
    import builtins
    assert 'test_ictr' in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )

def test_010_vend_debugger( structured_truck ):
    ''' Truck vends debugger with correct output. '''
    truck, capture = structured_truck
    debugger = truck( 0 )
    debugger( 'test' )
    assert capture.outputs == [ ( '__main__', 0, "TRACE0| test: 'test'" ) ]

def test_020_logging_recipe( log_capture ):
    ''' Logging recipe produces correct log output. '''
    from ictruck.recipes import produce_logging_truck
    truck = produce_logging_truck( install = False )
    truck( 'info' )( 'test' )
    assert "INFO:__main__:test" in log_capture.output.getvalue( )
    assert log_capture.records[ 0 ].levelname == 'INFO'

@pytest.mark.parametrize(
    'config, test_level, expected_enabled',
    [
        ( { 'trace_levels': { None: 1 } }, 1, True ),
        ( { 'trace_levels': { None: 1 } }, 2, False ),
        ( { 'trace_levels': { None: 1, 'test': 3 } }, 2, True ),
        ( { 'trace_levels': { None: 3, 'test': 1 } }, 2, False ),
        ( { 'trace_levels': { None: -1 } }, 0, False ),
    ],
    indirect = [ 'truck' ]
)
def test_100_trace_levels( truck, test_level, expected_enabled ):
    ''' Trace level calculations work correctly. '''
    truck_instance, _ = truck
    assert truck_instance( test_level ).enabled == expected_enabled

@pytest.mark.parametrize(
    'config, test_flavor, expected_enabled',
    [
        ( { 'active_flavors': { None: { 'debug' } } }, 'debug', True ),
        ( { 'active_flavors': { None: { 'debug' } } }, 'info', False ),
        ( { 'active_flavors': { None: { 'debug' }, 'test': { 'info' } } }, 'info', True ),
        ( { 'active_flavors': { None: { 'debug', 'error' }, 'test': { 'info' } } }, 'error', True ),
        ( { 'active_flavors': { } }, 'debug', False ),
    ],
    indirect = [ 'truck' ]
)
def test_110_active_flavors( truck, test_flavor, expected_enabled ):
    ''' Active flavor calculations work correctly. '''
    truck_instance, _ = truck
    assert truck_instance( test_flavor ).enabled == expected_enabled

@given(
    level = st.integers( min_value = -1, max_value = 10 ),
    flavor = st.integers( min_value = 0, max_value = 10 )
)
def test_200_trace_level_properties( level, flavor ):
    ''' Trace level properties hold for all inputs. '''
    truck, output = setup_truck( { 'trace_levels': { None: level } } )
    try:
        debugger = truck( flavor )
        assert debugger.enabled == ( flavor <= level )
    finally:
        output.close( )

def test_300_library_isolation( fs ):
    ''' Library registration does not affect global configuration. '''
    setup_filesystem(
        fs,
        'lib',
        "from ictruck import register_module\n"
        "from ictruck.configuration import Module, Flavor\n"
        "register_module( 'lib', configuration = Module( flavors = { 1: Flavor( ) } ) )" )
    sys.path.insert( 0, '/' )
    truck, output = setup_truck( { 'active_flavors': { None: { 'app' } } } )
    try:
        import_module( 'lib' )
        assert truck( 'app' ).enabled
        assert not truck( 1 ).enabled
        assert 'lib' in truck.modulecfgs
    finally:
        output.close( )

@pytest.mark.parametrize(
    'config',
    [ ( { 'trace_levels': { None: 5 } }, ) ],
    indirect = [ 'truck' ]
)
def test_400_thread_safety( truck, isolate_builtins ):
    ''' Truck is thread-safe under concurrent access. '''
    truck_instance, output = truck
    exceptions = [ ]
    def worker( ):
        try:
            for _ in range( 100 ):
                level = random.randint( 0, 10 )
                debugger = truck_instance( level )
                debugger( f"Test message from level {level}" )
                output.write( f"thread-{level}\n" )
        except Exception as e:
            exceptions.append( e )
    threads = [ threading.Thread( target = worker ) for _ in range( 10 ) ]
    for t in threads: t.start( )
    for t in threads: t.join( )
    assert not exceptions, "Exceptions in threads: {}".format( exceptions )
    assert output.getvalue( ).count( 'thread-' ) == 1000  # 10 threads * 100 iterations
```

## Conclusion

This testing strategy aligns with `ictruck`’s coding practices and test conventions, covering all modules (`exceptions`, `configuration`, `vehicles`) with a mix of unit, integration, isolation, and thread-safety tests. The use of `pyfakefs`, structured output/logging capture, and property-based testing ensures robustness, while maintaining high code coverage. The tests are organized into appropriately named modules with consistent naming and formatting. This plan should provide a solid foundation for ensuring the reliability of `icecream-truck`.
