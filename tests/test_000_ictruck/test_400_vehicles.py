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


import functools as funct
import warnings

import accretive as accret
import frigid as immut
import hypothesis
import pytest

from hypothesis import strategies as st

from . import PACKAGE_NAME, cache_import_module


valid_env_str = st.text(
    st.characters(
        codec='utf-8',
        exclude_characters=['\x00']  # Explicitly exclude null bytes
    )
)


@pytest.fixture( scope = 'session' )
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


@pytest.fixture( scope = 'session' )
def exceptions( ):
    ''' Provides exceptions module. '''
    return cache_import_module( f"{PACKAGE_NAME}.exceptions" )


@pytest.fixture( scope = 'session' )
def printers( ):
    ''' Provides printers module. '''
    return cache_import_module( f"{PACKAGE_NAME}.printers" )


@pytest.fixture( scope = 'session' )
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


@pytest.fixture
def mock_env( monkeypatch ):
    ''' Fixture for mocking environment variables. '''
    def _mock_env( env_dict ):
        for k, v in env_dict.items( ):
            monkeypatch.setenv( k, v )
    return _mock_env


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
def test_300_include_context_inheritance(
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
def test_310_prefix_inheritance(
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
def test_350_module_hierarchy(
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
    assert truck2.trace_levels == immut.Dictionary( levels )


def test_503_install_with_active_flavors( vehicles, clean_builtins ):
    ''' Installation configures active flavors correctly. '''
    truck1 = vehicles.install( active_flavors = { 'debug', 1, } )
    assert truck1.active_flavors[ None ] == { 'debug', 1, }
    flavors = { None: { 'x', }, 'test': { 'y', }, }
    truck2 = vehicles.install( alias = 'ictr2', active_flavors = flavors )
    expected = immut.Dictionary( {
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


def test_510_install_with_default_env_vars(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation respects default environment variable names. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', 'x.y:note,abort+z:success' )
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', '2+x.y:5' )
    truck = vehicles.install( printer_factory = simple_output )
    assert truck.active_flavors == immut.Dictionary( {
        'x.y': frozenset( { 'note', 'abort' } ),
        'z': frozenset( { 'success' } ) } )
    assert truck.trace_levels == immut.Dictionary( { None: 2, 'x.y': 5 } )


def test_511_install_with_custom_env_vars(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation uses custom environment variable names when provided. '''
    monkeypatch.setenv( 'CUSTOM_FLAVORS', 'test:errorx' )
    monkeypatch.setenv( 'CUSTOM_LEVELS', '3' )
    truck = vehicles.install(
        evname_active_flavors = 'CUSTOM_FLAVORS',
        evname_trace_levels = 'CUSTOM_LEVELS',
        printer_factory = simple_output )
    assert truck.active_flavors == (
        immut.Dictionary( { 'test': frozenset( { 'errorx' } ) } ) )
    assert truck.trace_levels == immut.Dictionary( { None: 3 } )


def test_512_install_with_env_vars_disabled(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation skips environment parsing when evname is None. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', 'x.y:foo' )
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', '4' )
    truck = vehicles.install(
        evname_active_flavors = None,
        evname_trace_levels = None,
        printer_factory = simple_output )
    assert truck.active_flavors == immut.Dictionary( { } )
    assert truck.trace_levels == immut.Dictionary( { None: -1 } )


def test_513_install_with_direct_args_overrides_env(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Direct arguments override environment parsing. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', 'x.y:note' )
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', '2' )
    truck = vehicles.install(
        active_flavors = { 'z': { 'success' } },
        trace_levels = { 'z': 1 },
        printer_factory = simple_output )
    assert truck.active_flavors == (
        immut.Dictionary( { 'z': frozenset( { 'success' } ) } ) )
    assert truck.trace_levels == immut.Dictionary( { None: -1, 'z': 1 } )


def test_514_produce_truck_with_env_vars(
    vehicles, simple_output, monkeypatch
):
    ''' Truck production respects environment when no direct args. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', 'global:debug' )
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', '0' )
    truck = vehicles.produce_truck( printer_factory = simple_output )
    assert truck.active_flavors == (
        immut.Dictionary( { 'global': frozenset( { 'debug' } ) } ) )
    assert truck.trace_levels == immut.Dictionary( { None: 0 } )


def test_515_install_global_scope_active_flavors_ev(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation parses global active flavors from environment. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', 'foo,bar' )
    truck = vehicles.install( printer_factory = simple_output )
    assert truck.active_flavors == (
        immut.Dictionary( { None: frozenset( { 'foo', 'bar' } ) } ) )


def test_516_install_wildcard_active_flavors_ev(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation parses wildcard active flavors from environment. '''
    monkeypatch.setenv( 'ICTRUCK_ACTIVE_FLAVORS', f"{__name__}:*" )
    truck = vehicles.install( printer_factory = simple_output )
    assert truck.active_flavors == (
        immut.Dictionary( { __name__: vehicles.omniflavor } ) )


def test_517_install_with_invalid_trace_levels(
    vehicles, clean_builtins, simple_output, monkeypatch
):
    ''' Installation skips invalid trace levels in environment. '''
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', 'abc+x.y:5+z:def' )
    with warnings.catch_warnings( record = True ) as records:
        truck = vehicles.install( printer_factory = simple_output )
    assert len( records ) == 2
    assert truck.trace_levels == immut.Dictionary( { None: -1, 'x.y': 5 } )


def test_518_produce_truck_with_invalid_global_trace_level(
    vehicles, simple_output, monkeypatch
):
    ''' Truck production skips invalid trace level in environment. '''
    monkeypatch.setenv( 'ICTRUCK_TRACE_LEVELS', 'invalid' )
    with warnings.catch_warnings( record = True ) as records:
        truck = vehicles.produce_truck( printer_factory = simple_output )
    assert len( records ) == 1
    assert truck.trace_levels == immut.Dictionary( { None: -1 } )


def test_600_register_module_basic(
    vehicles, configuration, printers, clean_builtins, simple_output
):
    ''' Module registration with defaults. '''
    printer_factory = funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        printer_factory = printer_factory,
        trace_levels = 0,
    ).install( )
    vehicles.register_module( )
    assert __name__ in truck.modulecfgs
    config = truck.modulecfgs[ __name__ ]
    assert isinstance( config, configuration.ModuleConfiguration )
    assert config.flavors == { }
    assert config.formatter_factory is None
    assert config.include_context is None
    assert config.prefix_emitter is None
    truck( 0 )( 'test' )
    output = simple_output.getvalue( )
    assert "TRACE0| 'test'" in output


def test_601_register_module_on_truck(
    vehicles, configuration, printers, clean_builtins, simple_output
):
    ''' Module registration on truck with defaults. '''
    printer_factory = funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        printer_factory = printer_factory,
        trace_levels = 0,
    ).install( )
    truck.register_module( )
    assert __name__ in truck.modulecfgs
    truck( 0 )( 'test' )
    output = simple_output.getvalue( )
    assert "TRACE0| 'test'" in output


def test_602_register_module_full_config_global(
    vehicles, configuration, printers, clean_builtins, simple_output
):
    ''' Module registration with all arguments. Global activation. '''
    printer_factory = funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        printer_factory = printer_factory,
        active_flavors = vehicles.omniflavor,
        trace_levels = 0,
    ).install( )
    flavors = { 'info': configuration.FlavorConfiguration( ) }
    def custom_formatter( ctrl, mname, flavor ):
        return lambda x: f"Custom: {x}"
    vehicles.register_module(
        name = __package__,
        flavors = flavors,
        formatter_factory = custom_formatter,
        include_context = False,
        prefix_emitter = 'Package| ' )
    vehicles.register_module( prefix_emitter = 'Module| ' )
    assert __package__ in truck.modulecfgs
    assert __name__ in truck.modulecfgs
    pconfig = truck.modulecfgs[ __package__ ]
    assert pconfig.flavors
    assert 'info' in pconfig.flavors
    assert pconfig.formatter_factory is custom_formatter
    assert pconfig.include_context is False
    assert pconfig.prefix_emitter == 'Package| '
    mconfig = truck.modulecfgs[ __name__ ]
    assert not mconfig.flavors
    assert mconfig.prefix_emitter == 'Module| '
    truck( 0 )( 'check' )
    truck( 'info' )( 'test' )
    output = simple_output.getvalue( )
    assert 'TRACE0| Custom: check' in output
    assert 'Module| Custom: test' in output


def test_603_register_module_full_config_package(
    vehicles, configuration, printers, clean_builtins, simple_output
):
    ''' Module registration with all arguments. Package-level activation. '''
    printer_factory = funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        printer_factory = printer_factory,
        active_flavors = { __package__: vehicles.omniflavor },
        trace_levels = { __package__: 0 },
    ).install( )
    flavors = { 'info': configuration.FlavorConfiguration( ) }
    def custom_formatter( ctrl, mname, flavor ):
        return lambda x: f"Custom: {x}"
    vehicles.register_module(
        name = __package__,
        flavors = flavors,
        formatter_factory = custom_formatter,
        include_context = False,
        prefix_emitter = 'Package| ' )
    vehicles.register_module( prefix_emitter = 'Module| ' )
    assert __package__ in truck.modulecfgs
    assert __name__ in truck.modulecfgs
    pconfig = truck.modulecfgs[ __package__ ]
    assert pconfig.flavors
    assert 'info' in pconfig.flavors
    assert pconfig.formatter_factory is custom_formatter
    assert pconfig.include_context is False
    assert pconfig.prefix_emitter == 'Package| '
    mconfig = truck.modulecfgs[ __name__ ]
    assert not mconfig.flavors
    assert mconfig.prefix_emitter == 'Module| '
    truck( 0 )( 'check' )
    truck( 'info' )( 'test' )
    output = simple_output.getvalue( )
    assert 'TRACE0| Custom: check' in output
    assert 'Module| Custom: test' in output


def test_610_register_module_auto_create( vehicles, clean_builtins ):
    ''' Module registration creates truck if none exists. '''
    import builtins
    vehicles.register_module( name = 'dummy1' )
    assert 'ictr' in builtins.__dict__
    assert isinstance( builtins.ictr, vehicles.Truck )
