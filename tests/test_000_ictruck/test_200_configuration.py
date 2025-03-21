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


import icecream
import pytest

from . import PACKAGE_NAME, cache_import_module


CLASS_NAMES = (
    'FlavorConfiguration', 'ModuleConfiguration', 'VehicleConfiguration' )


@pytest.fixture
def configuration( scope = 'session' ): # pylint: disable=unused-argument
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


def test_000_flavor_defaults( configuration ):
    ''' FlavorConfiguration has expected defaults. '''
    flavor = configuration.FlavorConfiguration( )
    assert flavor.formatter_factory is None
    assert flavor.include_context is None
    assert flavor.prefix_emitter is None


def test_001_module_defaults( configuration ):
    ''' ModuleConfiguration has expected defaults. '''
    module = configuration.ModuleConfiguration( )
    assert module.formatter_factory is None
    assert module.include_context is None
    assert module.prefix_emitter is None
    assert len( module.flavors ) == 0


def test_002_vehicle_defaults( configuration ):
    ''' VehicleConfiguration has expected defaults. '''
    vehicle = configuration.VehicleConfiguration( )
    assert callable( vehicle.formatter_factory )
    assert vehicle.include_context is False
    assert isinstance( vehicle.prefix_emitter, str )
    assert vehicle.prefix_emitter == icecream.DEFAULT_PREFIX
    assert len( vehicle.flavors ) == 10  # Default trace levels 0-9


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
def test_010_formatter_factory( configuration, class_name ):
    ''' Argument formatter_factory can be customized. '''
    # pylint: disable=unused-argument
    def custom_formatter( ctrl, mname, flavor ):
        return lambda arg: f'Custom: {arg}'
    # pylint: enable=unused-argument
    obj = getattr( configuration, class_name )(
        formatter_factory = custom_formatter )
    control = configuration.FormatterControl( )
    formatter = obj.formatter_factory( control, 'test', 0 )
    assert formatter( 'value' ) == 'Custom: value'


@pytest.mark.parametrize( 'class_name', CLASS_NAMES )
@pytest.mark.parametrize(
    'prefix_emitter, expected',
    [
        ( 'Custom| ', 'Custom| ' ),
        ( lambda ctrl, mname, flavor: 'Dynamic| ', 'Dynamic| ' ),
    ],
)
def test_020_prefix_emitter(
    configuration, class_name, prefix_emitter, expected
):
    ''' Argument prefix_emitter is string or callable. '''
    vehicle = getattr( configuration, class_name )(
        prefix_emitter = prefix_emitter )
    if isinstance( prefix_emitter, str ):
        assert vehicle.prefix_emitter == expected
    else:
        assert vehicle.prefix_emitter(
            configuration.FormatterControl( ), 'test', 0 ) == expected


def test_100_default_flavors( configuration ):
    ''' Vehicle provides default trace flavors 0-9. '''
    vehicle = configuration.VehicleConfiguration( )
    assert len( vehicle.flavors ) == 10
    for i in range( 10 ):
        assert vehicle.flavors[ i ].prefix_emitter == f'TRACE{i}| '
