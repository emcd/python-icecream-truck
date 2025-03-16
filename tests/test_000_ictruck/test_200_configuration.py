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

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


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
    assert vehicle.formatter is not None
    assert vehicle.include_context is False
    assert vehicle.prefix is not None
    assert len( vehicle.flavors ) == 10  # Default trace levels 0-9


@pytest.mark.parametrize(
    'prefix, expected',
    [ ( 'Custom| ', 'Custom| ' ) ],
)
def test_100_vehicle_prefix( prefix, expected, configuration ) -> None:
    ''' Vehicle prefix is None if not provided, custom if specified. '''
    vehicle = configuration.Vehicle( prefix = prefix )
    assert vehicle.prefix == expected, (
        f"Expected prefix '{expected}', got '{vehicle.prefix}'" )


@pytest.mark.parametrize(
    'prefix, expected',
    [ ( 'Module| ', 'Module| ' ) ],
)
def test_110_module_prefix( prefix, expected, configuration ) -> None:
    ''' Module prefix can be unset or custom. '''
    module = configuration.Module( prefix = prefix )
    assert module.prefix == expected, (
        f"Expected prefix '{expected}', got '{module.prefix}'" )


@pytest.mark.parametrize(
    'flavor_id, prefix, expected_prefix',
    [ ( 0, 'Custom| ', 'Custom| ' ) ],
)
def test_120_flavor_prefix(
    flavor_id, prefix, expected_prefix, configuration
) -> None:
    ''' Flavor prefix uses default trace prefix or custom override. '''
    flavor = configuration.Flavor( prefix = prefix )
    vehicle = configuration.Vehicle( flavors = { flavor_id: flavor } )
    assert vehicle.flavors[ flavor_id ].prefix == expected_prefix, (
        f"Expected prefix '{expected_prefix}', "
        f"got '{vehicle.flavors[ flavor_id ].prefix}'" )


def test_200_default_flavors( configuration ) -> None:
    ''' Vehicle provides default trace flavors 0-9. '''
    vehicle = configuration.Vehicle( )
    assert len( vehicle.flavors ) == 10, (
        f"Expected 10 flavors, got {len( vehicle.flavors )}" )
    for i in range( 10 ):
        expected = f'TRACE{i}| '
        assert vehicle.flavors[ i ].prefix == expected, (
            f"Flavor {i} expected prefix '{expected}', "
            f"got '{vehicle.flavors[ i ].prefix}'" )
