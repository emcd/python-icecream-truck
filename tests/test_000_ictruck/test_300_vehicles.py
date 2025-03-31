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


import hypothesis
import pytest

from hypothesis import strategies as st

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


def test_111_invalid_flavor_type( configuration, exceptions, vehicles ):
    ''' Passing invalid flavor type raises a validation error. '''
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ) )
    with pytest.raises( exceptions.ArgumentClassInvalidity ):
        truck( 3.14 )  # Float, neither int nor str


def test_112_flavor_unavailable(
    configuration, exceptions, vehicles
):
    ''' Undefined flavors raise FlavorInavailability. '''
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ),
        active_flavors = { None: { 'unknown' } } )
    with pytest.raises( exceptions.FlavorInavailability ):
        truck( 'unknown' )


def test_113_module_inference_failure(
    configuration, exceptions, vehicles, mocker
):
    ''' Module name discovery raises error when unresolvable. '''
    mocker.patch( 'inspect.getmodule', return_value = None )
    mocker.patch(
        'inspect.currentframe',
        return_value = mocker.Mock(
            f_code = mocker.Mock( co_filename = 'not_stdin' ) ) )
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ) )
    with pytest.raises( exceptions.ModuleInferenceFailure ):
        truck( 0 )


@pytest.mark.parametrize(
    'trace_levels, flavor, expected_enabled',
    [
        ( { None: 1 }, 0, True ),
        ( { None: 1 }, 2, False ),
        ( { None: -1 }, 0, False )
    ],
)
def test_120_trace_level_enablement(
    configuration, vehicles,
    trace_levels, flavor, expected_enabled,
):
    ''' Debugger enablement respects trace levels. '''
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ),
        trace_levels = trace_levels )
    debugger = truck( flavor )
    assert debugger.enabled == expected_enabled


@pytest.mark.parametrize(
    'active_flavors, flavor, expected_enabled',
    [
        ( { None: { 'debug' } }, 'debug', True ),
        ( { None: { 'info' } }, 'debug', False ),
        ( { __name__: { 'debug' } }, 'debug', True ),
    ],
)
def test_130_active_flavors_enablement(
    configuration, vehicles, active_flavors, flavor, expected_enabled,
):
    ''' Flavor enablement respects active_flavors for defined flavors. '''
    flavors = {
        'debug':
            configuration.FlavorConfiguration( prefix_emitter = 'DEBUG| ' ) }
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( flavors = flavors ),
        active_flavors = active_flavors )
    debugger = truck( flavor )
    assert debugger.enabled == expected_enabled


def test_140_formatter_factory_integration(
    configuration, vehicles, structured_capture
):
    ''' Formatter factory is correctly integrated into debugger. '''
    def custom_formatter( ctrl, mname, flavor ):
        return lambda arg: f'Formatted: {arg}'
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration(
            formatter_factory = custom_formatter ),
        printer_factory = structured_capture.printer_factory,
        trace_levels = { None: 1 } )
    debugger = truck( 0 )
    debugger( 'test' )
    output = structured_capture.outputs[ 0 ][ 2 ]
    assert output == 'TRACE0| Formatted: test'


def test_150_textio_printer( configuration, vehicles, simple_output ):
    ''' Printer factory as TextIOBase works correctly. '''
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ),
        printer_factory = simple_output,
        trace_levels = { None: 1 } )
    debugger = truck( 0 )
    debugger( 'test' )
    assert simple_output.getvalue( ).startswith( 'TRACE0| ' )


def test_200_debugger_cache( configuration, vehicles, structured_capture ):
    ''' Debugger caching works correctly with factories. '''
    truck = vehicles.Truck(
        generalcfg = configuration.VehicleConfiguration( ),
        printer_factory = structured_capture.printer_factory,
        trace_levels = { None: 1 } )
    debugger1 = truck( 0 )
    debugger1( 'test' )
    debugger2 = truck( 0 )
    assert debugger1 is debugger2
    assert len( structured_capture.outputs ) == 1


@hypothesis.given(
    vehicle_include = st.booleans( ),
    module_include = st.one_of( st.none( ), st.booleans( ) ),
    flavor_include = st.one_of( st.none( ), st.booleans( ) ),
)
def test_300_include_context_inheritance( # pylint: disable=too-many-locals
    configuration, vehicles,
    vehicle_include, module_include, flavor_include,
):
    ''' include_context inheritance follows flavor-specific precedence. '''
    flavors = { 0:
        configuration.FlavorConfiguration( include_context = flavor_include ) }
    generalcfg = configuration.VehicleConfiguration(
        include_context = vehicle_include, flavors = flavors )
    config = { 'generalcfg': generalcfg }
    if module_include is not None:
        config[ 'modulecfgs' ] = {
            __name__: configuration.ModuleConfiguration(
                include_context = module_include ) }
    truck = vehicles.Truck( **config )
    expected = (
        flavor_include if flavor_include is not None
        else (  module_include if module_include is not None
                else vehicle_include ) )
    ic_config = vehicles._produce_ic_configuration( truck, __name__, 0 )
    assert ic_config[ 'include_context' ] == expected


@pytest.mark.parametrize(
    'vehicle_prefix, module_prefix, flavor_on, flavor_prefix, expected',
    (
        ( 'V| ', None, 'vehicle', None, 'V| ' ),
        ( 'V| ', None, 'module', None, 'V| ' ),
        ( 'V| ', 'M| ', 'vehicle', None, 'M| ' ),
        ( 'V| ', 'M| ', 'module', None, 'M| ' ),
        ( 'V| ', None, 'vehicle', 'F| ', 'F| ' ),
        ( 'V| ', None, 'module', 'F| ', 'F| ' ),
        ( 'V| ', 'M| ', 'vehicle', 'F| ', 'F| ' ),
        ( 'V| ', 'M| ', 'module', 'F| ', 'F| ' ),
        ( lambda mname, flavor: 'V| ', None, 'vehicle', None, 'V| ' ),
        ( 'V| ', lambda mname, flavor: 'M| ', 'vehicle', None, 'M| ' ),
        ( 'V| ', 'M| ', 'vehicle', lambda mname, flavor: 'F| ', 'F| ' ),
    ),
)
def test_310_prefix_inheritance( # pylint: disable=too-many-arguments,too-many-locals
    configuration, vehicles, structured_capture,
    vehicle_prefix, module_prefix, flavor_on, flavor_prefix,
    expected,
):
    ''' Prefix inheritance respects precedence. '''
    flavorcfg = (
        configuration.FlavorConfiguration( prefix_emitter = flavor_prefix )
        if flavor_prefix is not None
        else configuration.FlavorConfiguration( ) )
    depth = 0
    flavors = { depth: flavorcfg }
    vehicle_initargs = dict( prefix_emitter = vehicle_prefix )
    module_initargs = { }
    if module_prefix is not None:
        module_initargs[ 'prefix_emitter' ] = module_prefix
    match flavor_on:
        case 'vehicle': vehicle_initargs[ 'flavors' ] = flavors
        case 'module':
            vehicle_initargs[ 'flavors' ] = { }
            module_initargs[ 'flavors' ] = flavors
    generalcfg = configuration.VehicleConfiguration( **vehicle_initargs )
    modulecfg = configuration.ModuleConfiguration( **module_initargs )
    config = {
        'generalcfg': generalcfg,
        'modulecfgs': { __name__: modulecfg },
        'trace_levels': { None: 1 } }
    truck = vehicles.Truck(
        printer_factory = structured_capture.printer_factory, **config )
    debugger = truck( depth )
    debugger( 'test' )
    assert len( structured_capture.outputs ) == 1
    _, _, output = structured_capture.outputs[ 0 ]
    assert output.startswith( expected )


@pytest.mark.parametrize(
    'module_name, parent_modules, flavor_overrides, expected_prefix',
    [
        ( 'x.y.z', { 'x': 'X| ', 'x.y': 'Y| ' },
            { }, 'TRACE0| ' ),
        ( 'x.y.z', { 'x': 'X| ', 'x.y': 'Y| ' },
            { 'x.y': 'Flavor| ' }, 'Flavor| ' ),
        ( 'a.b', { 'a': 'A| ' }, { }, 'TRACE0| ' ),
        ( 'p.q', { }, { }, 'TRACE0| ' ),
    ],
)
def test_350_module_hierarchy( # pylint: disable=too-many-arguments,too-many-locals
    configuration, vehicles,
    module_name, parent_modules, flavor_overrides, expected_prefix,
):
    ''' Module hierarchy respects flavor overrides with prefix_emitter. '''
    mconfigs = { }
    for mname, prefix in parent_modules.items( ):
        mc_nomargs = dict( prefix_emitter = prefix )
        if mname in flavor_overrides:
            mc_nomargs[ 'flavors' ] = { 0: configuration.FlavorConfiguration(
                prefix_emitter = flavor_overrides[ mname ] ) }
        mconfigs[ mname ] = configuration.ModuleConfiguration( **mc_nomargs )
    truck = vehicles.Truck( modulecfgs = mconfigs )
    ic_config = vehicles._produce_ic_configuration( truck, module_name, 0 )
    prefix_emitter = ic_config[ 'prefix_emitter' ]
    actual = (
        prefix_emitter if isinstance( prefix_emitter, str )
        else prefix_emitter(
            configuration.FormatterControl( ), module_name, 0 ) )
    assert actual == expected_prefix


def test_500_install_basic( vehicles, exceptions, clean_builtins ):
    ''' Basic installation into builtins with default alias. '''
    truck = vehicles.install( )
    import builtins
    assert 'ictr' in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )
    vehicles.install( )
    setattr( builtins, 'ictr', 'non-truck' )
    with pytest.raises( exceptions.AttributeNondisplacement ):
        vehicles.install( )


def test_501_install_custom_alias( vehicles, clean_builtins ):
    ''' Installation supports custom alias. '''
    alias = 'custom_truck'
    truck = vehicles.install( alias = alias )
    import builtins
    assert alias in builtins.__dict__
    assert builtins.__dict__[ alias ] is truck


def test_502_install_with_trace_levels( vehicles, clean_builtins ):
    ''' Installation configures trace levels correctly. '''
    truck1 = vehicles.install( trace_levels = 2 )
    assert truck1.trace_levels[ None ] == 2
    levels = { None: 1, 'test': 3, }
    truck2 = vehicles.install( alias = 'ictr2', trace_levels = levels )
    assert truck2.trace_levels == vehicles.__.ImmutableDictionary( levels )


def test_503_install_with_active_flavors( vehicles, clean_builtins ):
    ''' Installation configures active flavors correctly. '''
    truck1 = vehicles.install( active_flavors = { 'debug', 1, } )
    assert truck1.active_flavors[ None ] == { 'debug', 1, }
    flavors = { None: { 'x', }, 'test': { 'y', }, }
    truck2 = vehicles.install( alias = 'ictr2', active_flavors = flavors )
    expected = vehicles.__.ImmutableDictionary( {
        k: set( v ) for k, v in flavors.items( ) } )
    assert truck2.active_flavors == expected


def test_504_install_with_printer_factory(
    vehicles, clean_builtins, simple_output
):
    ''' Installation supports printer_factory as callable and TextIOBase. '''
    truck1 = vehicles.install( printer_factory = lambda m, f: print )
    assert callable( truck1.printer_factory )
    truck2 = vehicles.install(
        alias = 'ictr2', printer_factory = simple_output )
    assert isinstance( truck2.printer_factory, vehicles.__.io.TextIOBase )


def test_505_install_with_generalcfg(
    vehicles, clean_builtins, configuration
):
    ''' Installation supports custom vehicle configuration. '''
    generalcfg = configuration.VehicleConfiguration(
        prefix_emitter = 'foo:: ' )
    truck = vehicles.install( generalcfg = generalcfg )
    assert generalcfg is truck.generalcfg
    assert generalcfg.prefix_emitter == 'foo:: '


def test_506_install_preserves_module_configs(
    vehicles, configuration, clean_builtins, simple_output
):
    ''' Installing new truck preserves existing module configurations. '''
    # First installation with some module configs
    truck1 = vehicles.install( )
    flavors1 = {
        'lib1': configuration.FlavorConfiguration( prefix_emitter = 'LIB1| ' )
    }
    vehicles.register_module( name = 'library1', flavors = flavors1 )
    # Second installation with different settings
    # but should preserve module configs
    truck2 = vehicles.install(
        trace_levels = 3,
        printer_factory = simple_output )
    # Verify:
    # 1. New settings were applied
    assert truck2.trace_levels[ None ] == 3
    assert truck2.printer_factory is simple_output
    # 2. Module configs were preserved
    assert 'library1' in truck2.modulecfgs
    assert (
        truck2.modulecfgs[ 'library1' ].flavors[ 'lib1' ].prefix_emitter
        == 'LIB1| ' )
    # 3. The trucks are different instances
    assert truck1 is not truck2


def test_600_register_module_basic( vehicles, configuration, clean_builtins ):
    ''' Register module with explicit name and arguments. '''
    truck = vehicles.install( )
    flavors = {
        'test':
            configuration.FlavorConfiguration( prefix_emitter = 'Test| ' ) }
    vehicles.register_module( name = 'test_module', flavors = flavors )
    assert 'test_module' in truck.modulecfgs
    assert (
        truck .modulecfgs[ 'test_module' ]
        .flavors[ 'test' ].prefix_emitter == 'Test| ' )


def test_601_register_module_multiple(
    vehicles, configuration, clean_builtins, simple_output, monkeypatch
):
    ''' Register multiple modules with varying configurations. '''
    monkeypatch.setattr( 'sys.stderr', simple_output )
    truck = vehicles.install(
        trace_levels = { __package__: 0 }, active_flavors = { 'foo' } )
    vehicles.register_module( name = __package__ )  # Default config
    flavors = {
        'foo': configuration.FlavorConfiguration( prefix_emitter = 'foo:: ' ) }
    vehicles.register_module( name = __name__, flavors = flavors )
    truck( 0 )( 'test' )
    truck( 'foo' )( 'test' )
    output = simple_output.getvalue( )
    assert "TRACE0| 'test'" in output
    assert "foo:: 'test'" in output


def test_610_register_module_auto_name( vehicles, clean_builtins ):
    ''' Register module infers name from caller with custom prefix. '''
    truck = vehicles.install( )
    vehicles.register_module( prefix_emitter = 'Auto| ' )
    assert __name__ in truck.modulecfgs
    assert truck.modulecfgs[ __name__ ].prefix_emitter == 'Auto| '


def test_620_register_module_auto_create( vehicles, clean_builtins ):
    ''' Register module creates Truck if none exists. '''
    import builtins
    if 'ictr' in builtins.__dict__: del builtins.__dict__[ 'ictr' ]
    vehicles.register_module( )
    assert 'ictr' in builtins.__dict__
    assert isinstance( builtins.ictr, vehicles.Truck ) # pylint: disable=no-member
    assert builtins.ictr.printer_factory( 'm', 'f' )( None ) is None # pylint: disable=no-member


def test_630_register_module_absent_args(
    vehicles, configuration, clean_builtins
):
    ''' Register module handles absent arguments gracefully. '''
    truck = vehicles.install( )
    vehicles.register_module( )
    assert __name__ in truck.modulecfgs
    assert isinstance(
        truck.modulecfgs[ __name__ ], configuration.ModuleConfiguration )


def test_640_register_module_full_config( # pylint: disable=too-many-locals
    vehicles, configuration, clean_builtins, simple_output, monkeypatch
):
    ''' Register module with all arguments configured. '''
    monkeypatch.setattr( 'sys.stderr', simple_output )
    truck = vehicles.install( trace_levels = 0, active_flavors = { 'info' } )
    flavors = { 'info': configuration.FlavorConfiguration( ) }
    def custom_formatter( ctrl, mname, flavor ):
        return lambda x: f"Custom: {x}"
    vehicles.register_module(
        name = __name__,
        flavors = flavors,
        formatter_factory = custom_formatter,
        include_context = False,
        prefix_emitter = 'Full| ' )
    debugger = truck( 'info' )
    debugger( 'test' )
    output = simple_output.getvalue( )
    assert 'Full| Custom: test' in output
    assert __name__ not in output


def test_650_register_module_absent_config(
    vehicles, configuration, clean_builtins
):
    ''' Register module with absent configuration uses default. '''
    truck = vehicles.install( )
    truck.register_module( )
    assert __name__ in truck.modulecfgs
    config = truck.modulecfgs[ __name__ ]
    assert isinstance( config, configuration.ModuleConfiguration )
    assert config.flavors == { }
