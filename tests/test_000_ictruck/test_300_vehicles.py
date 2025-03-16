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

# pylint: disable=unused-argument


import pytest

from hypothesis import given, strategies as st

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture( scope = 'session' )
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


@pytest.fixture( scope = 'session' )
def exceptions( ):
    ''' Provides exceptions module. '''
    return cache_import_module( f"{PACKAGE_NAME}.exceptions" )


@pytest.fixture( scope = 'session' )
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


@pytest.mark.parametrize(
    'vehicle_prefix, module_prefix, flavor_prefix, expected',
    [
        ( 'Vehicle| ', None, None, 'TRACE0| ' ),
        ( 'Vehicle| ', 'Module| ', None, 'TRACE0| ' ),
        ( 'Vehicle| ', None, 'Flavor| ', 'Flavor| ' ),
        ( 'Vehicle| ', 'Module| ', 'Flavor| ', 'Flavor| ' ),
    ]
)
def test_100_prefix_inheritance( # pylint: disable=too-many-arguments,too-many-locals
    vehicle_prefix, module_prefix, flavor_prefix, expected,
    configuration, vehicles, structured_capture
) -> None:
    test_flavor = 0
    if flavor_prefix is not None:
        flavors = {
            test_flavor: configuration.Flavor( prefix = flavor_prefix ) }
        vehicle_cfg = configuration.Vehicle(
            prefix = vehicle_prefix, flavors = flavors )
    else:
        vehicle_cfg = configuration.Vehicle( prefix = vehicle_prefix )
    config = {
        'generalcfg': vehicle_cfg,
        'trace_levels': { None: 1 },
    }
    if module_prefix is not None:
        module_cfg = configuration.Module( prefix = module_prefix )
        config[ 'modulecfgs' ] = { __name__: module_cfg }
    truck = vehicles.Truck(
        printer_factory = structured_capture.printer_factory,
        **config )
    debugger = truck( test_flavor )
    assert debugger.enabled, (
        f"Debugger for flavor {test_flavor} should be enabled" )
    debugger( 'test' )
    assert len( structured_capture.outputs ) == 1, 'Expected one output entry'
    mname, flavor, output = structured_capture.outputs[ 0 ]
    assert mname == __name__, f"Expected module name '{__name__}', got {mname}"
    assert flavor == test_flavor, (
        f"Expected flavor {test_flavor}, got {flavor}" )
    assert output.startswith( expected ), (
        f"Output '{output}' should start with '{expected}'" )
    assert output.endswith( "'test'" ), (
        f"Output '{output}' should end with \"'test'\"" )


@pytest.mark.parametrize(
    'trace_levels, flavor, expected_enabled',
    [
        ( { None: 1 }, 0, True ),
        ( { None: 1 }, 2, False ),
        ( { None: -1 }, 0, False ),
    ]
)
def test_110_trace_level_enablement(
    trace_levels, flavor, expected_enabled, configuration, vehicles
) -> None:
    ''' Debugger enablement respects trace levels. '''
    config = {
        'generalcfg': configuration.Vehicle( ),
        'trace_levels': trace_levels,
    }
    truck = vehicles.Truck( **config )
    debugger = truck( flavor )
    assert debugger.enabled == expected_enabled, (
        f"Flavor {flavor} enabled should be {expected_enabled}, "
        f"got {debugger.enabled}" )


def test_120_module_inference_failure( configuration, vehicles, mocker ):
    ''' Module name discovery raises error when unresolvable. '''
    mocker.patch( 'inspect.getmodule', return_value = None )
    mocker.patch(
        'inspect.currentframe',
        return_value = mocker.Mock(
            f_code = mocker.Mock( co_filename = 'not_stdin' ) ) )
    truck = vehicles.Truck( generalcfg = configuration.Vehicle( ) )
    with pytest.raises( vehicles._exceptions.ModuleInferenceFailure ):
        truck( 0 )


@pytest.mark.parametrize(
    'active_flavors, flavor, expected_enabled',
    [
        ( { None: { 'debug' } }, 'debug', True ),
        ( { None: { 'info' } }, 'debug', False ),
        ( { __name__: { 'debug' } }, 'debug', True ),
    ]
)
def test_130_string_flavor_enablement(
    active_flavors, flavor, expected_enabled, configuration, vehicles
) -> None:
    ''' Flavor enablement respects active_flavors for defined flavors. '''
    flavors = { 'debug': configuration.Flavor( prefix = 'DEBUG| ' ) }
    config = {
        'generalcfg': configuration.Vehicle( flavors = flavors ),
        'active_flavors': active_flavors,
    }
    truck = vehicles.Truck( **config )
    debugger = truck( flavor )
    assert debugger.enabled == expected_enabled, (
        f"Flavor '{flavor}' enabled should be {expected_enabled}, "
        f"got {debugger.enabled}" )


def test_131_string_flavor_unavailable( configuration, vehicles ):
    ''' Undefined string flavors raise FlavorInavailability. '''
    config = {
        'generalcfg': configuration.Vehicle( ),
        'active_flavors': { None: { 'unknown' } },
    }
    truck = vehicles.Truck( **config )
    with pytest.raises(
        vehicles._exceptions.FlavorInavailability
    ) as exc_info: truck( 'unknown' )
    assert str( exc_info.value ) == "Flavor 'unknown' is not available."


def test_140_textio_printer( configuration, vehicles ):
    ''' Printer factory as TextIOBase works correctly. '''
    from io import StringIO
    output = StringIO( )
    truck = vehicles.Truck(
        generalcfg = configuration.Vehicle( ),
        printer_factory = output,
        trace_levels = { None: 1 } )
    debugger = truck( 0 )
    debugger( 'test' )
    assert output.getvalue( ).startswith( 'TRACE0| ' )


@pytest.mark.parametrize(
    'vehicle_flavor_prefix, module_flavor_prefix, expected',
    [
        ( 'VehicleFlavor| ', 'ModuleFlavor| ', 'ModuleFlavor| ' ),
        ( 'VehicleFlavor| ', None, 'VehicleFlavor| ' ),
    ]
)
def test_150_module_flavor_override( # pylint: disable=too-many-arguments,too-many-locals
    vehicle_flavor_prefix, module_flavor_prefix, expected,
    configuration, vehicles, structured_capture
) -> None:
    ''' Module flavor overrides vehicle flavor. '''
    test_flavor = 0
    vehicle_flavors = {
        test_flavor: configuration.Flavor( prefix = vehicle_flavor_prefix ) }
    vehicle_cfg = configuration.Vehicle( flavors = vehicle_flavors )
    config = {
        'generalcfg': vehicle_cfg,
        'trace_levels': { None: 1 },
    }
    if module_flavor_prefix is not None:
        module_flavors = {
            test_flavor:
                configuration.Flavor( prefix = module_flavor_prefix ) }
        config[ 'modulecfgs' ] = {
            __name__: configuration.Module( flavors = module_flavors ) }
    truck = vehicles.Truck(
        printer_factory = structured_capture.printer_factory, **config )
    debugger = truck( test_flavor )
    debugger( 'test' )
    output = structured_capture.outputs[ 0 ][ 2 ]
    assert output.startswith( expected )


@given(
    vehicle_include = st.booleans( ),
    module_include = st.one_of( st.none( ), st.booleans( ) ),
    flavor_include = st.one_of( st.none( ), st.booleans( ) )
)
def test_200_include_context_inheritance( # pylint: disable=too-many-locals
    vehicle_include, module_include, flavor_include, configuration, vehicles
) -> None:
    ''' include_context inheritance follows flavor-specific precedence. '''
    flavors = { 0: configuration.Flavor( include_context = flavor_include ) }
    vehicle_cfg = (
        configuration.Vehicle(
            include_context = vehicle_include, flavors = flavors ) )
    config = { 'generalcfg': vehicle_cfg }
    if module_include is not None:
        module_cfg = configuration.Module( include_context = module_include )
        config[ 'modulecfgs' ] = { __name__: module_cfg }
    truck = vehicles.Truck( **config )
    expected = (
        flavor_include if flavor_include is not None else vehicle_include )
    ic_config = vehicles._produce_ic_configuration( truck, __name__, 0 )
    assert ic_config[ 'include_context' ] == expected, (
        f"Expected {expected}, got {ic_config['include_context']} with "
        f"vehicle_include={vehicle_include}, module_include={module_include}, "
        f"flavor_include={flavor_include}" )


@pytest.mark.parametrize(
    'module_name, parent_modules, flavor_overrides, expected_prefix',
    [
        ( 'x.y.z', { 'x': 'X| ', 'x.y': 'Y| ' },
            { }, 'TRACE0| ' ),
        ( 'x.y.z', { 'x': 'X| ', 'x.y': 'Y| ' },
            { 'x.y': 'Flavor| ' }, 'Flavor| ' ),
        ( 'a.b', { 'a': 'A| ' }, { }, 'TRACE0| ' ),
        ( 'p.q', { }, { }, 'TRACE0| ' ),
    ]
)
def test_300_module_hierarchy( # pylint: disable=too-many-arguments,too-many-locals
    module_name, parent_modules, flavor_overrides, expected_prefix,
    configuration, vehicles
) -> None:
    ''' Module hierarchy respects flavor overrides. '''
    module_configs = { }
    for mod_name, prefix in parent_modules.items( ):
        module_configs[ mod_name ] = configuration.Module( prefix = prefix )
    for mod_name, flavor_prefix in flavor_overrides.items( ):
        module_configs[ mod_name ].flavors[ 0 ] = (
            configuration.Flavor( prefix = flavor_prefix ) )
    config = { 'modulecfgs': module_configs }
    truck = vehicles.Truck( **config )
    ic_config = vehicles._produce_ic_configuration( truck, module_name, 0 )
    assert ic_config[ 'prefix' ] == expected_prefix


def test_400_debugger_cache( configuration, vehicles, structured_capture ):
    ''' Debugger caching works correctly. '''
    truck = vehicles.Truck(
        generalcfg = configuration.Vehicle( ),
        printer_factory = structured_capture.printer_factory,
        trace_levels = { None: 1 } )
    debugger1 = truck( 0 )
    debugger1( 'test' )
    assert len( structured_capture.outputs ) == 1
    debugger2 = truck( 0 )
    assert debugger1 is debugger2  # Same instance

def test_410_invalid_flavor_type( configuration, vehicles, exceptions ):
    ''' Passing invalid flavor type raises a validation error. '''
    truck = vehicles.Truck( generalcfg = configuration.Vehicle( ) )
    with pytest.raises( exceptions.ArgumentClassInvalidity ):
        truck( 3.14 )  # Float, neither int nor str


def test_500_install_basic( vehicles, clean_builtins ):
    ''' Basic installation adds Truck to builtins with default alias. '''
    truck = vehicles.install( )
    import builtins
    assert 'ictr' in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )


def test_510_install_custom_alias( vehicles, clean_builtins ):
    ''' Installation supports custom alias. '''
    alias = 'custom_truck'
    truck = vehicles.install( alias = alias )
    import builtins
    assert alias in builtins.__dict__
    assert builtins.__dict__[ alias ] is truck


def test_520_install_with_trace_levels( vehicles, clean_builtins ):
    ''' Installation configures trace levels correctly. '''
    truck1 = vehicles.install( trace_levels = 2 )
    assert truck1.trace_levels[ None ] == 2
    levels = { None: 1, 'test': 3, }
    truck2 = vehicles.install( trace_levels = levels )
    assert truck2.trace_levels == vehicles.__.ImmutableDictionary( levels )


def test_530_install_with_active_flavors( vehicles, clean_builtins ):
    ''' Installation configures active flavors correctly. '''
    truck1 = vehicles.install( active_flavors = { 'debug', 1, } )
    assert truck1.active_flavors[ None ] == { 'debug', 1, }
    flavors = { None: { 'x', }, 'test': { 'y', }, }
    truck2 = vehicles.install( active_flavors = flavors )
    expected = vehicles.__.ImmutableDictionary( {
        k: set( v ) for k, v in flavors.items( ) } )
    assert truck2.active_flavors == expected


def test_540_install_with_printer_factory(
    vehicles, clean_builtins, simple_output
):
    ''' Installation supports printer_factory as callable and TextIOBase. '''
    truck1 = vehicles.install( printer_factory = lambda m, f: print )
    assert callable( truck1.printer_factory )
    truck2 = vehicles.install( printer_factory = simple_output )
    assert isinstance( truck2.printer_factory, vehicles.__.io.TextIOBase )


def test_550_install_with_generalcfg(
    vehicles, clean_builtins, configuration
):
    ''' Installation supports custom vehicle configuration. '''
    generalcfg = configuration.Vehicle( prefix = 'foo:: ' )
    truck = vehicles.install( generalcfg = generalcfg )
    assert generalcfg is truck.generalcfg
    assert generalcfg.prefix == 'foo:: '


def test_600_register_module_basic( vehicles, configuration, clean_builtins ):
    ''' Register module with explicit name and configuration. '''
    truck = vehicles.install( )
    module_cfg = configuration.Module( prefix = 'Test| ' )
    vehicles.register_module(
        name = 'test_module', configuration = module_cfg )
    assert 'test_module' in truck.modulecfgs
    assert truck.modulecfgs[ 'test_module' ] is module_cfg


def test_601_register_module_multiple(
    vehicles, configuration, clean_builtins
):
    ''' Register multiple modules. '''
    truck = vehicles.install(
        trace_levels = { __package__: 0, __name__: -1 } )
    vehicles.register_module( name = __package__ )
    modulecfg = configuration.Module(
        flavors = { 'foo': configuration.Flavor( prefix = 'foo:: ' ) } )
    vehicles.register_module( name = __name__, configuration = modulecfg )
    truck( 0 )( 'test' )
    truck( 'foo' )( 'test' )


def test_610_register_module_auto_name(
    vehicles, configuration, clean_builtins
):
    ''' Register module infers name from caller. '''
    truck = vehicles.install( )
    vehicles.register_module(
        configuration = configuration.Module( prefix = 'Auto| ' ) )
    assert __name__ in truck.modulecfgs
    assert truck.modulecfgs[ __name__ ].prefix == 'Auto| '


def test_620_register_module_auto_create( vehicles, clean_builtins ):
    ''' Register module creates Truck if none exists. '''
    import builtins
    if 'ictr' in builtins.__dict__:
        del builtins.__dict__[ 'ictr' ]
    vehicles.register_module( )
    assert 'ictr' in builtins.__dict__
    # pylint: disable=no-member
    assert isinstance( builtins.ictr, vehicles.Truck )
    assert builtins.ictr.printer_factory( 'm', 'f' )( None ) is None
    # pylint: enable=no-member


def test_630_register_module_absent_args(
    vehicles, configuration, clean_builtins
):
    ''' Register module handles absent arguments gracefully. '''
    truck = vehicles.install( )
    vehicles.register_module( )
    assert __name__ in truck.modulecfgs
    assert isinstance( truck.modulecfgs[ __name__ ], configuration.Module )
