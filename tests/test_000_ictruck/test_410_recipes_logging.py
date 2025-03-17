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


''' Tests for recipes module. '''

# pylint: disable=unused-argument


import logging

import pytest

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture( scope = 'session' )
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


@pytest.fixture( scope = 'session' )
def recipes( ):
    ''' Provides recipes module. '''
    return cache_import_module( f"{PACKAGE_NAME}.recipes.logging" )


@pytest.fixture( scope = 'session' )
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


def test_000_produce_logging_truck_default(
    recipes, vehicles, log_capture, clean_builtins
):
    ''' Default produce_logging_truck installs truck in builtins. '''
    truck = recipes.produce_logging_truck( )
    import builtins
    assert 'ictr' in builtins.__dict__, "Truck not installed in builtins"
    assert isinstance( truck, vehicles.Truck ), "Not a Truck instance"
    debugger = truck( 'info' )
    debugger( 'test message' )
    assert any(
        r.levelno == logging.INFO and 'test message' in r.getMessage( )
        for r in log_capture.records ), "Logging not captured"


def test_010_produce_logging_truck_no_install(
    recipes, vehicles, log_capture
):
    ''' produce_logging_truck with install=False does not affect builtins. '''
    import builtins
    original = dict( builtins.__dict__ )
    truck = recipes.produce_logging_truck( install = False )
    assert builtins.__dict__ == original, "Builtins modified unexpectedly"
    assert isinstance( truck, vehicles.Truck ), "Not a Truck instance"
    debugger = truck( 'debug' )
    debugger( 'debug test' )
    assert any(
        r.levelno == logging.DEBUG and 'debug test' in r.getMessage( )
        for r in log_capture.records ), "Debug logging not captured"


def test_020_produce_logging_truck_flavors( recipes, clean_builtins ):
    ''' produce_logging_truck sets expected active flavors. '''
    truck = recipes.produce_logging_truck( install = False )
    expected_flavors = { 'debug', 'info', 'warning', 'error', 'critical' }
    assert None in truck.active_flavors, "No global active flavors"
    assert truck.active_flavors[ None ] == expected_flavors, (
        f"Expected {expected_flavors}, got {truck.active_flavors[None]}" )
    for flavor in expected_flavors:
        debugger = truck( flavor )
        assert debugger.enabled, f"Flavor '{flavor}' should be enabled"


def test_030_produce_logging_truck_generalcfg(
    recipes, configuration, clean_builtins
):
    ''' produce_logging_truck configures generalcfg with flavors. '''
    truck = recipes.produce_logging_truck( install = False )
    assert isinstance( truck.generalcfg, configuration.Vehicle ), (
        "generalcfg not a Vehicle instance" )
    assert set( truck.generalcfg.flavors.keys( ) ) == (
        { 'debug', 'info', 'warning', 'error', 'critical' } ), (
        "Unexpected flavors in generalcfg" )
    for flavor in truck.generalcfg.flavors:
        assert isinstance(
            truck.generalcfg.flavors[ flavor ], configuration.Flavor ), (
                f"Flavor '{flavor}' not a Flavor instance" )


def test_040_logger_factory_string_flavors( recipes, log_capture ):
    ''' _logger_factory handles string flavors correctly. '''
    for flavor in ( 'debug', 'info', 'warning', 'error', 'critical' ):
        printer = recipes._logger_factory( 'test_module', flavor )
        printer( f"{flavor} test" )
        expected_level = getattr( logging, flavor.upper( ) )
        assert any(
            r.levelno == expected_level and f"{flavor} test" in r.getMessage( )
            for r in log_capture.records ), f"{flavor} not logged correctly"
        log_capture.clear( )


def test_050_logger_factory_int_flavor( recipes, log_capture ):
    ''' _logger_factory defaults to DEBUG for integer flavors. '''
    printer = recipes._logger_factory( 'test_module', 42 )
    printer( 'int flavor test' )
    assert any(
        r.levelno == logging.DEBUG and 'int flavor test' in r.getMessage( )
        for r in log_capture.records ), "Integer flavor not logged as DEBUG"


def test_060_logger_factory_module_name( recipes, log_capture ):
    ''' _logger_factory uses correct module name in logger. '''
    module_name = 'custom.module'
    printer = recipes._logger_factory( module_name, 'error' )
    printer( 'module test' )
    assert any(
        r.name == module_name and 'module test' in r.getMessage( )
        for r in log_capture.records ), "Module name not in log record"
