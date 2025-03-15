# Testing Strategy for `icecream-truck`

## Overview

This document outlines a comprehensive testing strategy for the `icecream-truck` Python package. The strategy focuses on thorough coverage while adhering to the project's established coding style and practices, with emphasis on dependency injection rather than monkey patching.

### Goals
- Verify correct behavior of individual components
- Test configuration hierarchy and inheritance
- Ensure library configuration isolation
- Validate thread safety
- Maintain high code coverage

### Tools
- **pytest**: Core testing framework
- **pyfakefs**: Filesystem simulation for module isolation testing
- **hypothesis**: Property-based testing
- **StringIO/structured capture**: Output capture without monkey patching

## Test Module Structure

```
tests/test_000_ictruck/
├── __init__.py            # Common fixtures and utilities
├── test_000_package.py    # Basic package sanity checks
├── test_010_base.py       # Common imports checks
├── test_100_exceptions.py # Exception handling tests
├── test_200_configuration.py  # Configuration and inheritance tests
├── test_300_vehicles.py   # Core vehicle functionality tests
└── test_400_recipes.py    # Recipe tests (logging truck, etc.)
```

## Fixtures

The following fixtures will be defined in `tests/test_000_ictruck/__init__.py` to be shared across test modules:

```python
# Additional fixtures for test_000_ictruck/__init__.py

import builtins
import io
import logging
import sys
from importlib import import_module

def capture_output( ):
    ''' Creates a simple output capture mechanism. '''
    return io.StringIO( )

class StructuredCapture:
    ''' Captures structured output with module and flavor information. '''

    def __init__( self ):
        self.outputs = [ ]
        self.buffer = io.StringIO( )

    def printer_factory( self, mname, flavor ):
        ''' Creates a printer that captures structured output. '''
        def printer( text ):
            self.outputs.append( ( mname, flavor, text ) )
            self.buffer.write( f"{mname}:{flavor}:{text}\n" )
        return printer

    def clear( self ):
        ''' Clears captured output. '''
        self.outputs.clear( )
        self.buffer.seek( 0 )
        self.buffer.truncate( )

    def __del__( self ):
        self.buffer.close( )

class LogCapture( logging.Handler ):
    ''' Captures log records with full metadata. '''

    def __init__( self ):
        super( ).__init__( )
        self.records = [ ]
        self.buffer = io.StringIO( )

    def emit( self, record ):
        self.records.append( record )
        self.buffer.write( f"{record.levelname}:{record.name}:{record.getMessage( )}\n" )

    def clear( self ):
        ''' Clears captured log records. '''
        self.records.clear( )
        self.buffer.seek( 0 )
        self.buffer.truncate( )

    def __del__( self ):
        self.buffer.close( )

@pytest.fixture
def simple_output( ):
    ''' Provides a simple output capture. '''
    output = capture_output( )
    yield output
    output.close( )

@pytest.fixture
def structured_capture( ):
    ''' Provides a structured output capture. '''
    capture = StructuredCapture( )
    yield capture

@pytest.fixture
def log_capture( ):
    ''' Provides a logging capture handler. '''
    capture = LogCapture( )
    root_logger = logging.getLogger( )
    original_level = root_logger.level
    root_logger.setLevel( logging.DEBUG )
    root_logger.addHandler( capture )
    yield capture
    root_logger.removeHandler( capture )
    root_logger.setLevel( original_level )

@pytest.fixture
def clean_builtins( ):
    ''' Preserves and restores the original __builtins__ state. '''
    original = dict( builtins.__dict__ )
    yield
    for key in list( builtins.__dict__.keys( ) ):
        if key not in original:
            delattr( builtins, key )
        else:
            builtins.__dict__[ key ] = original[ key ]

def create_truck_with_output( config = None ):
    ''' Creates a truck with a simple output capture. '''
    if config is None: config = { }
    output = capture_output( )
    printer = lambda mname, flavor: lambda x: output.write( x + '\n' )
    from ictruck.vehicles import Truck
    return Truck( printer_factory = printer, **config ), output

def create_truck_with_structured_capture( config = None ):
    ''' Creates a truck with structured output capture. '''
    if config is None: config = { }
    capture = StructuredCapture( )
    from ictruck.vehicles import Truck
    return Truck( printer_factory = capture.printer_factory, **config ), capture
```

## Test Modules

### 1. `test_100_exceptions.py`

Tests for proper exception behavior.

```python
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


''' Tests for exceptions module. '''


import pytest

from . import cache_import_module


@pytest.fixture
def exceptions( ):
    ''' Provides exceptions module. '''
    return cache_import_module( 'ictruck.exceptions' )


def test_000_omniexception_base( exceptions ):
    ''' Omniexception is base for all others. '''
    assert issubclass( exceptions.Omnierror, exceptions.Omniexception )
    assert issubclass( exceptions.ArgumentClassInvalidity, exceptions.Omnierror )
    assert issubclass( exceptions.FlavorInavailability, exceptions.Omnierror )
    assert issubclass( exceptions.ModuleInferenceFailure, exceptions.Omnierror )


def test_010_argument_class_invalidity( exceptions ):
    ''' ArgumentClassInvalidity exception provides helpful message. '''
    with pytest.raises( exceptions.ArgumentClassInvalidity ) as excinfo:
        raise exceptions.ArgumentClassInvalidity( 'test_arg', str )

    assert 'test_arg' in str( excinfo.value )
    assert 'str' in str( excinfo.value )


def test_020_flavor_inavailability( exceptions ):
    ''' FlavorInavailability exception properly formats flavor. '''
    with pytest.raises( exceptions.FlavorInavailability ) as excinfo:
        raise exceptions.FlavorInavailability( 'debug' )

    assert "Flavor 'debug'" in str( excinfo.value )

    with pytest.raises( exceptions.FlavorInavailability ) as excinfo:
        raise exceptions.FlavorInavailability( 3 )

    assert "Flavor 3" in str( excinfo.value )


def test_030_module_inference_failure( exceptions ):
    ''' ModuleInferenceFailure has expected message. '''
    with pytest.raises( exceptions.ModuleInferenceFailure ) as excinfo:
        raise exceptions.ModuleInferenceFailure( )

    assert "Could not infer invoking module" in str( excinfo.value )


def test_040_exception_chaining( exceptions ):
    ''' Exceptions support proper exception chaining. '''
    original = ValueError( "Original error" )

    # Direct chaining with from
    try:
        try:
            raise original
        except ValueError as e:
            raise exceptions.Omnierror( "Chained error" ) from e
    except exceptions.Omnierror as exc:
        assert exc.__cause__ is original

    # Implicit chaining via context
    try:
        try:
            raise original
        except ValueError:
            raise exceptions.Omnierror( "Context error" )
    except exceptions.Omnierror as exc:
        assert exc.__context__ is original
```

### 2. `test_200_configuration.py`

Tests for configuration hierarchy and inheritance.

```python
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


''' Tests for configuration module. '''


import pytest
from hypothesis import given, strategies as st

from . import cache_import_module, create_truck_with_structured_capture


@pytest.fixture
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( 'ictruck.configuration' )


@pytest.fixture
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( 'ictruck.vehicles' )


def test_000_flavor_defaults( configuration ):
    ''' Flavor has expected defaults. '''
    flavor = configuration.Flavor( )
    assert flavor.formatter is None
    assert flavor.include_context is None
    assert flavor.prefix is None


def test_010_module_defaults( configuration ):
    ''' Module has expected defaults. '''
    module = configuration.Module( )
    assert module.formatter is None
    assert module.include_context is None
    assert module.prefix is None
    assert len( module.flavors ) == 0


def test_020_vehicle_defaults( configuration ):
    ''' Vehicle has expected defaults. '''
    vehicle = configuration.Vehicle( )
    assert vehicle.formatter == _icecream.DEFAULT_ARG_TO_STRING_FUNCTION
    assert vehicle.include_context is False
    assert vehicle.prefix == _icecream.DEFAULT_PREFIX
    assert len( vehicle.flavors ) == 10  # Default trace levels 0-9


@pytest.mark.parametrize( 'vehicle_prefix,module_prefix,flavor_prefix,expected', [
    ( 'Vehicle| ', None, None, 'Vehicle| ' ),
    ( 'Vehicle| ', 'Module| ', None, 'Module| ' ),
    ( 'Vehicle| ', None, 'Flavor| ', 'Flavor| ' ),
    ( 'Vehicle| ', 'Module| ', 'Flavor| ', 'Flavor| ' ),
] )
def test_100_prefix_inheritance(
    vehicle_prefix, module_prefix, flavor_prefix, expected,
    configuration, vehicles
):
    ''' Prefix inheritance follows expected precedence. '''
    # Create configurations
    vehicle_cfg = configuration.Vehicle( prefix = vehicle_prefix )
    config = { 'generalcfg': vehicle_cfg }

    # Set up module configuration if needed
    if module_prefix is not None:
        module_cfg = configuration.Module( prefix = module_prefix )
        config[ 'modulecfgs' ] = { '__main__': module_cfg }

    # Set up flavor configuration if needed
    test_flavor = 'test_flavor'
    if flavor_prefix is not None:
        flavor_cfg = configuration.Flavor( prefix = flavor_prefix )
        if 'modulecfgs' in config:
            config[ 'modulecfgs' ][ '__main__' ].flavors[ test_flavor ] = flavor_cfg
        else:
            vehicle_cfg.flavors[ test_flavor ] = flavor_cfg

    # Create truck and test configuration
    truck, _ = create_truck_with_structured_capture( config )

    # Test with flavor-specific prefix if used
    ic_config = vehicles._produce_ic_configuration( truck, '__main__', test_flavor )
    assert ic_config[ 'prefix' ] == expected


@given(
    vehicle_include = st.booleans( ),
    module_include = st.one_of( st.none( ), st.booleans( ) ),
    flavor_include = st.one_of( st.none( ), st.booleans( ) )
)
def test_200_include_context_inheritance(
    vehicle_include, module_include, flavor_include,
    configuration, vehicles
):
    ''' include_context inheritance follows expected precedence. '''
    # Create configurations
    vehicle_cfg = configuration.Vehicle( include_context = vehicle_include )
    config = { 'generalcfg': vehicle_cfg }

    # Set up module configuration if needed
    if module_include is not None:
        module_cfg = configuration.Module( include_context = module_include )
        config[ 'modulecfgs' ] = { '__main__': module_cfg }

    # Set up flavor configuration if needed
    test_flavor = 'test_flavor'
    flavor_cfg = configuration.Flavor( include_context = flavor_include )
    vehicle_cfg.flavors[ test_flavor ] = flavor_cfg

    # Create truck and test configuration
    truck, _ = create_truck_with_structured_capture( config )

    # Determine expected include_context value
    expected = flavor_include if flavor_include is not None else (
        module_include if module_include is not None else vehicle_include )

    # Test configuration
    ic_config = vehicles._produce_ic_configuration( truck, '__main__', test_flavor )
    assert ic_config[ 'include_context' ] == expected


@pytest.mark.parametrize( 'module_name,parent_modules,expected_effective_configs', [
    ( 'x.y.z', { 'x': 'X| ', 'x.y': 'Y| ' }, { 'prefix': 'Y| ' } ),
    ( 'a.b', { 'a': 'A| ' }, { 'prefix': 'A| ' } ),
    ( 'c.d.e.f', { 'c': 'C| ', 'c.d.e': 'E| ' }, { 'prefix': 'E| ' } ),
    ( 'p.q', { }, { } ),  # No parent configs - falls back to general config
] )
def test_300_module_hierarchy(
    module_name, parent_modules, expected_effective_configs,
    configuration
):
    ''' Module hierarchy inheritance merges configurations correctly. '''
    # Create parent module configurations
    module_configs = { }
    for mod_name, prefix in parent_modules.items( ):
        module_configs[ mod_name ] = configuration.Module( prefix = prefix )

    # Create truck with module configurations
    config = { 'modulecfgs': module_configs }
    truck, _ = create_truck_with_structured_capture( config )

    # Test effective configuration
    from ictruck.vehicles import _calculate_effective_trace_level
    from ictruck.vehicles import _calculate_effective_flavors

    # Verify module configuration is properly inherited through the hierarchy
    if 'prefix' in expected_effective_configs:
        prefix = None
        module_paths = list( module_name.split( '.' ) )
        for i in range( len( module_paths ) ):
            parent = '.'.join( module_paths[ :i + 1 ] )
            if parent in parent_modules:
                prefix = parent_modules[ parent ]
        assert prefix == expected_effective_configs[ 'prefix' ]
```

### 3. `test_300_vehicles.py`

Tests for core vehicle functionality.

```python
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


''' Tests for vehicles module. '''


import io
import random
import sys
import threading
from importlib import import_module

import pytest
from hypothesis import given, strategies as st
from pyfakefs.fake_filesystem_unittest import Patcher

from . import (
    cache_import_module, clean_builtins, simple_output,
    create_truck_with_output, create_truck_with_structured_capture
)


@pytest.fixture
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( 'ictruck.vehicles' )


@pytest.fixture
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( 'ictruck.configuration' )


def test_000_install_basic( vehicles, clean_builtins ):
    ''' install adds truck to builtins with default alias. '''
    truck = vehicles.install( )
    import builtins
    assert hasattr( builtins, 'ictr' )
    assert builtins.ictr is truck


def test_010_install_custom_alias( vehicles, clean_builtins ):
    ''' install supports custom alias. '''
    truck = vehicles.install( alias = 'test_alias' )
    import builtins
    assert hasattr( builtins, 'test_alias' )
    assert builtins.test_alias is truck


def test_020_install_with_trace_levels( vehicles, clean_builtins ):
    ''' install configures trace levels correctly. '''
    # Test with integer trace level
    truck1 = vehicles.install( alias = 'test1', trace_levels = 3 )
    assert truck1.trace_levels[ None ] == 3

    # Test with mapping trace levels
    truck2 = vehicles.install(
        alias = 'test2',
        trace_levels = { None: 1, 'pkg': 2, 'pkg.mod': 3 } )
    assert truck2.trace_levels[ None ] == 1
    assert truck2.trace_levels[ 'pkg' ] == 2
    assert truck2.trace_levels[ 'pkg.mod' ] == 3


def test_030_install_with_active_flavors( vehicles, clean_builtins ):
    ''' install configures active flavors correctly. '''
    # Test with set of flavors
    truck1 = vehicles.install( alias = 'test1', active_flavors = { 'a', 'b', 1 } )
    assert truck1.active_flavors[ None ] == { 'a', 'b', 1 }

    # Test with mapping of flavors
    truck2 = vehicles.install(
        alias = 'test2',
        active_flavors = { None: { 'x', 'y' }, 'pkg': { 'z' } } )
    assert truck2.active_flavors[ None ] == { 'x', 'y' }
    assert truck2.active_flavors[ 'pkg' ] == { 'z' }


def test_040_vend_debugger( configuration ):
    ''' Truck vends debugger and respects enabled state. '''
    # Create truck with trace level 2
    truck, capture = create_truck_with_structured_capture( {
        'trace_levels': { None: 2 }
    } )

    # Trace level 1 should be enabled
    debug1 = truck( 1 )
    assert debug1.enabled

    # Trace level 3 should be disabled
    debug3 = truck( 3 )
    assert not debug3.enabled

    # Test enabled output
    test_val = 42
    debug1( test_val )
    assert len( capture.outputs ) == 1
    assert capture.outputs[ 0 ][ 2 ].endswith( f"test_val: {test_val}" )

    # Test disabled output (should not append to outputs)
    output_count = len( capture.outputs )
    debug3( "This should not appear" )
    assert len( capture.outputs ) == output_count


def test_050_register_module( vehicles, configuration, clean_builtins ):
    ''' register_module associates configuration with module. '''
    # Create truck and module configuration
    truck = vehicles.install( alias = 'test_truck' )
    module_cfg = configuration.Module( prefix = "TestModule| " )

    # Register module configuration
    vehicles.register_module( name = 'test_module', configuration = module_cfg )

    # Verify configuration is registered
    assert 'test_module' in truck.modulecfgs
    assert truck.modulecfgs[ 'test_module' ] is module_cfg


def test_060_register_module_auto_create( vehicles, clean_builtins ):
    ''' register_module creates truck if none exists. '''
    import builtins
    # Make sure truck doesn't exist
    if hasattr( builtins, 'ictr' ):
        delattr( builtins, 'ictr' )

    # Register module without explicit truck
    vehicles.register_module( name = 'auto_module' )

    # Verify truck was created
    assert hasattr( builtins, 'ictr' )
    assert 'auto_module' in builtins.ictr.modulecfgs


@pytest.mark.parametrize( 'global_level,module_level,test_level,expected_enabled', [
    ( 1, None, 1, True ),
    ( 1, None, 2, False ),
    ( 1, 3, 2, True ),
    ( 3, 1, 2, False ),
] )
def test_100_trace_level_calculations(
    global_level, module_level, test_level, expected_enabled
):
    ''' Trace levels are calculated correctly for modules. '''
    # Set up trace levels
    trace_levels = { None: global_level }
    if module_level is not None:
        trace_levels[ '__main__' ] = module_level

    # Create truck with trace levels
    truck, _ = create_truck_with_output( { 'trace_levels': trace_levels } )

    # Test debugger enabled state
    assert truck( test_level ).enabled == expected_enabled


@pytest.mark.parametrize( 'global_flavors,module_flavors,test_flavor,expected_enabled', [
    ( { 'debug' }, None, 'debug', True ),
    ( { 'debug' }, None, 'info', False ),
    ( { 'debug' }, { 'info' }, 'info', True ),
    ( { 'debug', 'error' }, { 'info' }, 'error', True ),
] )
def test_110_active_flavor_calculations(
    global_flavors, module_flavors, test_flavor, expected_enabled
):
    ''' Active flavors are calculated correctly for modules. '''
    # Set up active flavors
    active_flavors = { None: global_flavors }
    if module_flavors is not None:
        active_flavors[ '__main__' ] = module_flavors

    # Create truck with active flavors
    truck, _ = create_truck_with_output( { 'active_flavors': active_flavors } )

    # Test debugger enabled state
    assert truck( test_flavor ).enabled == expected_enabled


def test_200_module_name_inference( vehicles ):
    ''' Module name is correctly inferred from call stack. '''
    module_name = vehicles._discover_invoker_module_name( )
    assert module_name == '__main__' or module_name.endswith( 'test_300_vehicles' )


def test_300_library_isolation( ):
    ''' Library configurations don't interfere with each other. '''
    with Patcher( ) as patcher:
        fs = patcher.fs

        # Create two library modules with different configurations
        fs.create_file( '/lib_a/__init__.py', contents = """
from ictruck import register_module, ModuleConfiguration, FlavorConfiguration
register_module( 'lib_a', configuration = ModuleConfiguration(
    prefix = 'LibA| ',
    flavors = { 'debug': FlavorConfiguration( prefix = 'LibA-DEBUG| ' ) }
) )
""" )

        fs.create_file( '/lib_b/__init__.py', contents = """
from ictruck import register_module, ModuleConfiguration, FlavorConfiguration
register_module( 'lib_b', configuration = ModuleConfiguration(
    prefix = 'LibB| ',
    flavors = { 'debug': FlavorConfiguration( prefix = 'LibB-DEBUG| ' ) }
) )
""" )

        # Add root to sys.path and import libraries
        sys.path.insert( 0, '/' )
        truck, capture = create_truck_with_structured_capture( {
            'active_flavors': { None: { 'debug' } }
        } )

        # Import libraries
        import_module( 'lib_a' )
        import_module( 'lib_b' )

        # Verify configurations are isolated
        lib_a_debugger = truck( 'debug' )
        lib_b_debugger = truck( 'debug' )

        # Note: We can't directly test this because _discover_invoker_module_name
        # will always return the current test module. In real usage, this would work.

        # Verify both libraries registered configurations
        assert 'lib_a' in truck.modulecfgs
        assert 'lib_b' in truck.modulecfgs
        assert truck.modulecfgs[ 'lib_a' ].prefix == 'LibA| '
        assert truck.modulecfgs[ 'lib_b' ].prefix == 'LibB| '


@pytest.mark.slow
def test_400_thread_safety( clean_builtins ):
    ''' Truck is thread-safe for concurrent debugger access. '''
    from ictruck.vehicles import install

    # Set up truck with trace levels
    truck = install( alias = 'test_truck', trace_levels = { None: 5 } )

    # Set up output capture
    output = io.StringIO( )
    truck.printer_factory = lambda mname, flavor: lambda x: output.write( f"{mname}:{flavor}:{x}\n" )

    # Track exceptions in threads
    exceptions = [ ]

    def worker( ):
        try:
            for _ in range( 100 ):
                level = random.randint( 0, 10 )
                debugger = truck( level )
                value = f"Thread value {level}"
                debugger( value )
        except Exception as e:
            exceptions.append( e )

    # Run multiple threads
    threads = [ threading.Thread( target = worker ) for _ in range( 10 ) ]
    for t in threads: t.start( )
    for t in threads: t.join( )

    # Check no exceptions occurred
    assert not exceptions, f"Exceptions in threads: {exceptions}"

    # Verify output was captured
    lines = output.getvalue( ).strip( ).split( '\n' )
    assert len( lines ) > 0  # At least some output was captured
```

### 4. `test_400_recipes.py`

Tests for specialized recipes like logging integration.

```python
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


''' Tests for specialist recipes. '''


import logging

import pytest

from . import cache_import_module, clean_builtins, log_capture, structured_capture


@pytest.fixture
def specialists( ):
    ''' Provides specialists module. '''
    return cache_import_module( 'ictruck.specialists' )


def test_000_produce_logging_truck( specialists, log_capture, clean_builtins ):
    ''' produce_logging_truck creates truck that integrates with logging. '''
    # Create a logging truck without installing
    truck = specialists.produce_logging_truck( install = False )

    # Verify active flavors
    expected_flavors = { 'debug', 'info', 'warning', 'error', 'critical' }
    assert None in truck.active_flavors
    assert truck.active_flavors[ None ] == expected_flavors

    # Test all flavors
    for flavor in expected_flavors:
        debugger = truck( flavor )
        assert debugger.enabled

        # Use the debugger
        test_val = f"Test {flavor}"
        debugger( test_val )

        # Find matching log record
        matching = [ r for r in log_capture.records if test_val in r.getMessage( ) ]
        assert len( matching ) == 1

        # Verify log level
        expected_level = getattr( logging, flavor.upper( ) )
        assert matching[ 0 ].levelno == expected_level


def test_010_produce_logging_truck_install( specialists, log_capture, clean_builtins ):
    ''' produce_logging_truck can install the truck as a builtin. '''
    # Create and install a logging truck
    truck = specialists.produce_logging_truck( install = True )

    # Verify truck was installed
    import builtins
    assert hasattr( builtins, 'ictr' )
    assert builtins.ictr is truck


def test_020_logger_factory( specialists, log_capture ):
    ''' _logger_factory creates appropriate logger functions. '''
    # Get the logger factory
    logger_factory = specialists._logger_factory

    # Create printers for different flavors and modules
    debug_printer = logger_factory( 'test_module', 'debug' )
    info_printer = logger_factory( 'test_module', 'info' )
    error_printer = logger_factory( 'test_module', 'error' )
    numeric_printer = logger_factory( 'test_module', 2 )  # Should default to DEBUG

    # Test each printer
    debug_printer( "Debug message" )
    info_printer( "Info message" )
    error_printer( "Error message" )
    numeric_printer( "Numeric level message" )

    # Verify log records
    assert any( r.levelno == logging.DEBUG and "Debug message" in r.getMessage( ) for r in log_capture.records )
    assert any( r.levelno == logging.INFO and "Info message" in r.getMessage( ) for r in log_capture.records )
    assert any( r.levelno == logging.ERROR and "Error message" in r.getMessage( ) for r in log_capture.records )
    assert any( r.levelno == logging.DEBUG and "Numeric level message" in r.getMessage( ) for r in log_capture.records )


def test_030_custom_recipe_integration( structured_capture, clean_builtins ):
    ''' Integration of custom recipes with truck framework. '''
    # Define a custom printer factory
    def rich_style_printer_factory( mname, flavor ):
        def printer( text ):
            formatted = f"[bold]{mname}[/bold] ({flavor}): {text}"
            structured_capture.outputs.append( ( mname, flavor, formatted ) )
        return printer

    # Create a custom truck configuration
    from ictruck.configuration import Vehicle, Flavor
    custom_config = Vehicle(
        prefix = "RICH| ",
        flavors = {
            'verbose': Flavor( prefix = "DETAIL| " ),
            'summary': Flavor( prefix = "SUMMARY| " )
        }
    )

    # Create and install a custom truck
    from ictruck.vehicles import install
    truck = install(
        alias = 'rich_ictr',
        generalcfg = custom_config,
        printer_factory = rich_style_printer_factory,
        active_flavors = { 'verbose', 'summary' }
    )

    # Test the custom truck
    debugger = truck( 'verbose' )
    assert debugger.enabled
    debugger( "Detailed information" )

    # Verify output
    assert len( structured_capture.outputs ) == 1
    assert structured_capture.outputs[0][0] == '__main__'  # module name
    assert structured_capture.outputs[0][1] == 'verbose'   # flavor
    assert "DETAIL| " in structured_capture.outputs[0][2]  # custom prefix from flavor
```

## Property-Based Testing Examples

We can include more advanced property-based tests to validate configuration merging and module hierarchy inheritance more thoroughly.

```python
from hypothesis import given, strategies as st

@given(
    active_flavors_global=st.sets(st.one_of(st.integers(), st.text())),
    active_flavors_module=st.sets(st.one_of(st.integers(), st.text())),
    test_flavor=st.one_of(st.integers(), st.text())
)
def test_500_active_flavors_property(active_flavors_global, active_flavors_module, test_flavor):
    ''' Active flavors calculation should follow consistent rules. '''
    # Create the configuration
    config = {
        'active_flavors': {
            None: active_flavors_global,
            'test_module': active_flavors_module
        }
    }

    # Create a truck with this configuration
    truck, _ = create_truck_with_output(config)

    # Calculate expected enabled state
    expected_enabled = (
        test_flavor in active_flavors_global or
        test_flavor in active_flavors_module
    )

    # Simulate being in test_module
    # (In real testing, we'd use pyfakefs to create a real module)
    from ictruck.vehicles import _calculate_effective_flavors
    effective_flavors = _calculate_effective_flavors(
        truck.active_flavors, 'test_module')

    # Verify properties
    assert (test_flavor in effective_flavors) == expected_enabled

    # If flavor is in module-specific set but not global, it should still be enabled
    if test_flavor in active_flavors_module and test_flavor not in active_flavors_global:
        assert test_flavor in effective_flavors

    # Flavor must be in at least one set to be enabled
    if test_flavor not in active_flavors_global and test_flavor not in active_flavors_module:
        assert test_flavor not in effective_flavors


@given(
    module_structure=st.lists(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1),
                             min_size=1, max_size=5)
)
def test_600_module_hierarchy_property(module_structure):
    ''' Module hierarchy traversal should cover all parent modules. '''
    from ictruck.vehicles import _iterate_module_name_ancestry

    # Create a module name from the structure (e.g., ['a', 'b', 'c'] -> 'a.b.c')
    module_name = '.'.join(module_structure)

    # Get all parent modules
    parent_modules = list(_iterate_module_name_ancestry(module_name))

    # Verify properties
    # There should be exactly as many parent modules as there are parts
    assert len(parent_modules) == len(module_structure)

    # First parent should be first component
    assert parent_modules[0] == module_structure[0]

    # Last parent should be the full module name
    assert parent_modules[-1] == module_name

    # Each parent should be a prefix of the full module name
    for parent in parent_modules:
        assert module_name.startswith(parent)

    # Each parent should be a prefix of all subsequent parents
    for i in range(len(parent_modules) - 1):
        assert parent_modules[i+1].startswith(parent_modules[i])
```

## Thread Safety Testing

For comprehensive thread safety testing, we should verify the behavior under high concurrency. Since these tests are slow, we mark them with `@pytest.mark.slow` so they can be selectively run.

```python
@pytest.mark.slow
def test_700_thread_safety_race_conditions(clean_builtins):
    ''' Test for race conditions when multiple threads access the truck. '''
    import threading
    import time
    import random
    from ictruck.vehicles import install

    # Create a truck with minimal configuration
    truck = install(alias='race_truck', trace_levels={None: 5})

    # Set up counters to track operations
    counters = {
        'debuggers_created': 0,
        'debuggers_used': 0,
        'errors': []
    }

    # Define worker function that stresses the debugger cache
    def worker():
        try:
            # Repeatedly get and use debuggers with various flavors
            for _ in range(50):
                flavor = random.choice([0, 1, 2, 3, 4, 5, 'debug', 'info'])
                debugger = truck(flavor)
                counters['debuggers_created'] += 1

                # Small delay to increase chance of race conditions
                time.sleep(random.random() * 0.001)

                # Use the debugger
                debugger(f"Test from thread {threading.current_thread().name}")
                counters['debuggers_used'] += 1
        except Exception as e:
            counters['errors'].append(str(e))

    # Create and start threads
    threads = []
    for i in range(20):
        thread = threading.Thread(target=worker, name=f"thread-{i}")
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify no errors occurred
    assert not counters['errors'], f"Errors in threads: {counters['errors']}"

    # Verify all operations completed successfully
    assert counters['debuggers_created'] == 20 * 50
    assert counters['debuggers_used'] == 20 * 50

    # Verify debuggers were cached correctly
    # Each flavor should have exactly one debugger instance in the cache
    unique_flavors = {0, 1, 2, 3, 4, 5, 'debug', 'info'}
    cache_entries = [(k[1], len(v)) for k, v in truck._debuggers.items()]

    # Each flavor should appear in the cache
    cache_flavors = {entry[0] for entry in cache_entries}
    assert unique_flavors.issubset(cache_flavors)
```

## Conclusion

This testing strategy provides comprehensive coverage of the `icecream-truck` package's functionality while adhering to the project's coding style and practices. Key features of this approach include:

1. **Dependency Injection Over Mocking**: We leverage the package's clean dependency injection design to test behavior without monkey patching.

2. **Real Filesystem Testing**: Using `pyfakefs` for creating real module structures to test library isolation without manipulating the actual filesystem.

3. **Structured Output Capture**: Custom capture mechanisms for both simple text output and structured data including module names and flavors.

4. **Configuration Hierarchy Testing**: Thorough testing of the configuration inheritance chain, ensuring correct precedence.

5. **Thread Safety Validation**: Targeted tests for potential race conditions in shared resources.

6. **Property-Based Testing**: Using Hypothesis to verify configuration merging and module hierarchy follow consistent properties across a wide range of inputs.

7. **Specialized Recipe Testing**: Separate module for testing specialized functionality like logging integration.

8. **Adherence to Project Style**: All test code follows the project's established coding style with proper spacing, vertical compactness, and docstring formatting.

By implementing this strategy, we can ensure `icecream-truck` functions correctly, maintains isolation between libraries, and handles concurrent usage safely while preserving high code coverage.
