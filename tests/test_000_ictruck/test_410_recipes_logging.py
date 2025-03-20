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


def test_011_logger_factory_string_flavors( recipes, log_capture ):
    ''' Printer factory handles string flavors correctly. '''
    for flavor in ( 'debug', 'info', 'warning', 'error', 'critical' ):
        printer = recipes.produce_printer( 'test_module', flavor )
        printer( f"{flavor} test" )
        expected_level = getattr( logging, flavor.upper( ) )
        assert any(
            r.levelno == expected_level and f"{flavor} test" in r.getMessage( )
            for r in log_capture.records )
        log_capture.clear( )


def test_012_logger_factory_int_flavor( recipes, log_capture ):
    ''' Printer factory defaults to DEBUG for integer flavors. '''
    printer = recipes.produce_printer( 'test_module', 42 )
    printer( 'int flavor test' )
    assert any(
        r.levelno == logging.DEBUG and 'int flavor test' in r.getMessage( )
        for r in log_capture.records )


def test_013_logger_factory_module_name( recipes, log_capture ):
    ''' Printer factory uses correct module name in logger. '''
    module_name = 'custom.module'
    printer = recipes.produce_printer( module_name, 'error' )
    printer( 'module test' )
    assert any(
        r.name == module_name and 'module test' in r.getMessage( )
        for r in log_capture.records )


def test_101_produce_truck_flavors( recipes, clean_builtins ):
    ''' Truck factory sets expected active flavors. '''
    truck = recipes.produce_truck( )
    expected_flavors = { 'debug', 'info', 'warning', 'error', 'critical' }
    assert None in truck.active_flavors
    assert truck.active_flavors[ None ] == expected_flavors
    for flavor in expected_flavors:
        debugger = truck( flavor )
        assert debugger.enabled


def test_102_produce_truck_generalcfg(
    recipes, configuration, clean_builtins
):
    ''' Truck factory configures generalcfg with flavors. '''
    truck = recipes.produce_truck( )
    assert isinstance( truck.generalcfg, configuration.VehicleConfiguration )
    assert set( truck.generalcfg.flavors.keys( ) ) == (
        { 'debug', 'info', 'warning', 'error', 'critical' } )
    for flavor in truck.generalcfg.flavors:
        assert isinstance(
            truck.generalcfg.flavors[ flavor ],
            configuration.FlavorConfiguration )


def test_200_install_truck_default(
    recipes, vehicles, log_capture, clean_builtins
):
    ''' Basic installation into builtins with default alias. '''
    truck = recipes.install( )
    import builtins
    assert 'ictr' in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )
    debugger = truck( 'info' )
    debugger( 'test message' )
    assert any(
        r.levelno == logging.INFO and 'test message' in r.getMessage( )
        for r in log_capture.records )


def test_201_install_truck_custom_alias( recipes, clean_builtins ):
    ''' Installation supports custom alias. '''
    alias = 'custom_truck'
    recipes.install( alias = alias )
    import builtins
    assert alias in builtins.__dict__


def test_202_install_debuggers( recipes, clean_builtins ):
    ''' Installation of aliased debuggers. '''
    aliases = dict(
        icd = 'debug', ici = 'info', icw = 'warning',
        ice = 'error', icc = 'critical' )
    recipes.install( additional_aliases = aliases )
    import builtins
    for alias in aliases: assert alias in builtins.__dict__
