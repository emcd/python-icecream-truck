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


''' Tests for rich recipes module. '''

# pylint: disable=unused-argument


import sys

import pytest
from rich.console import Console

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture( scope = 'session' )
def base( ):
    ''' Provides base utilities module. '''
    return cache_import_module( f"{PACKAGE_NAME}.__" )


@pytest.fixture( scope = 'session' )
def configuration( ):
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


@pytest.fixture( scope = 'session' )
def recipes( ):
    ''' Provides rich recipes module. '''
    return cache_import_module( f"{PACKAGE_NAME}.recipes.rich" )


@pytest.fixture( scope = 'session' )
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


def test_011_console_formatter_output( recipes, simple_output ):
    ''' Console formatter produces expected rich output. '''
    console = Console( file = simple_output, force_terminal = True )
    formatter = recipes._produce_console_formatter(
        console, None, 'test_module', 1 )
    value = { 'key': 'value' }
    result = formatter( value )
    assert 'key' in result and 'value' in result
    assert '\n' in result  # Rich formatting includes newlines


def test_012_simple_printer_output( recipes, simple_output ):
    ''' Simple printer outputs text to target stream. '''
    printer = (
        recipes._produce_simple_printer(
            simple_output, 'test_module', 1 ) )
    text = "Test output"
    printer( text )
    assert simple_output.getvalue( ) == "Test output\n"


def test_013_simple_printer_stderr( recipes, simple_output, monkeypatch ):
    ''' Simple printer respects stderr target. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    printer = (
        recipes._produce_simple_printer( sys.stderr, 'test_module', 1 ) )
    text = "Error output"
    printer( text )
    assert simple_output.getvalue( ) == "Error output\n"


def test_014_console_text_io_invalidity( recipes, monkeypatch ):
    ''' Producing truck with invalid IO raises exception. '''
    from unittest.mock import Mock
    invalid_stream = Mock( spec = [ ] )  # Mock with no TextIOBase methods
    monkeypatch.setattr( sys, 'stdout', invalid_stream )
    with pytest.raises( recipes.ConsoleTextIoInvalidity ):
        recipes.produce_truck( stderr = False, trace_levels = 3 )


def test_101_produce_truck_default(
    recipes, base, vehicles, simple_output, monkeypatch
):
    ''' Truck factory produces truck with default settings. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.produce_truck( trace_levels = 0 )  # Enable trace level 0
    assert isinstance( truck, vehicles.Truck )
    assert isinstance( truck.generalcfg.formatter_factory, base.funct.partial )
    debugger = truck( 0 )
    debugger( "Test trace" )
    output = simple_output.getvalue( )
    assert "Test trace" in output


def test_102_produce_truck_trace_levels(
    recipes, vehicles, simple_output, monkeypatch
):
    ''' Truck factory respects trace levels. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.produce_truck( trace_levels = 2 )
    assert truck.trace_levels[ None ] == 2
    debugger0 = truck( 0 )
    debugger1 = truck( 1 )
    debugger2 = truck( 2 )
    debugger3 = truck( 3 )
    debugger0( "Trace 0" )
    debugger1( "Trace 1" )
    debugger2( "Trace 2" )
    debugger3( "Trace 3" )
    output = simple_output.getvalue( )
    assert "Trace 0" in output
    assert "Trace 1" in output
    assert "Trace 2" in output
    assert "Trace 3" not in output  # Disabled due to trace level


def test_103_produce_truck_active_flavors( # pylint: disable=too-many-locals
    recipes, base, vehicles, simple_output, monkeypatch
):
    ''' Truck factory respects active flavors. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    flavors = base.AccretiveDictionary(
        info = vehicles._FlavorConfiguration( ),
        error = vehicles._FlavorConfiguration( ),
        debug = vehicles._FlavorConfiguration( ) )
    truck = recipes.produce_truck(
        flavors = flavors,
        active_flavors = { 'info', 'error' }
    )
    assert truck.active_flavors[ None ] == { 'info', 'error' }
    debugger_info = truck( 'info' )
    debugger_error = truck( 'error' )
    debugger_debug = truck( 'debug' )
    debugger_info( "Info message" )
    debugger_error( "Error message" )
    debugger_debug( "Debug message" )
    output = simple_output.getvalue( )
    assert "Info message" in output
    assert "Error message" in output
    assert "Debug message" not in output  # Disabled due to inactive flavor


def test_200_install_truck_default(
    recipes, vehicles, simple_output, clean_builtins, monkeypatch
):
    ''' Basic installation into builtins with default alias. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.install( trace_levels = 0 )  # Enable trace level 0
    import builtins
    assert 'ictr' in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )
    debugger = truck( 0 )
    debugger( "Installed test" )
    assert "Installed test" in simple_output.getvalue( )


def test_201_install_truck_custom_alias( recipes, vehicles, clean_builtins ):
    ''' Installation supports custom alias. '''
    alias = 'rich_truck'
    truck = recipes.install( alias = alias )
    import builtins
    assert alias in builtins.__dict__
    assert isinstance( truck, vehicles.Truck )


def test_202_install_truck_trace_levels(
    recipes, vehicles, simple_output, clean_builtins, monkeypatch
):
    ''' Installation respects trace levels. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.install( trace_levels = 1 )
    debugger0 = truck( 0 )
    debugger1 = truck( 1 )
    debugger2 = truck( 2 )
    debugger0( "Trace 0" )
    debugger1( "Trace 1" )
    debugger2( "Trace 2" )
    output = simple_output.getvalue( )
    assert "Trace 0" in output
    assert "Trace 1" in output
    assert "Trace 2" not in output
