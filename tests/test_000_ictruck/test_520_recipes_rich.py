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


def test_011_console_formatter_output( recipes, configuration, simple_output ):
    ''' Console formatter produces expected rich output. '''
    console = Console( file = simple_output, force_terminal = True )
    formatter = recipes.produce_console_formatter(
        console, configuration.FormatterControl( ), 'test', 1 )
    value = { 'key': 'value' }
    result = formatter( value )
    assert 'key' in result and 'value' in result
    assert '\n' in result  # Rich formatting includes newlines


def test_012_console_printer_output( recipes, simple_output ):
    ''' Console printer outputs text with Rich styling. '''
    console = Console( file = simple_output, force_terminal = True )
    printer = recipes.produce_console_printer( console, 'test', 1 )
    text = "Rich output"
    printer( text )
    output = simple_output.getvalue( )
    assert "Rich output" in output
    assert '\n' in output  # Rich console adds newline


# def test_014_pretty_formatter_output( recipes, configuration ):
#     ''' Pretty formatter produces plain-text pretty output. '''
#     formatter = recipes.produce_pretty_formatter(
#         configuration.FormatterControl( ), 'test', 1 )
#     # Force multi-line output by limiting width
#     formatter = lambda x: formatter( x, max_width = 10 )
#     value = { 'a': [ 1, 2, 3 ], 'b': 'test' }
#     result = formatter( value )
#     assert "'a': [1, 2, 3]" in result  # Pretty-printed structure
#     assert "'b': 'test'" in result
#     assert '\n' in result  # Multi-line output


def test_015_console_text_io_invalidity( recipes, monkeypatch ):
    ''' Producing truck with invalid IO raises exception. '''
    from unittest.mock import Mock
    invalid_stream = Mock( spec = [ ] )
    monkeypatch.setattr( sys, 'stdout', invalid_stream )
    with pytest.raises( recipes.ConsoleTextIoInvalidity ):
        recipes.produce_truck( stderr = False )


def test_101_produce_truck_formatter_mode(
    recipes, base, vehicles, simple_output, monkeypatch
):
    ''' Truck in Formatter mode uses console formatter and simple printer. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.produce_truck(
        mode = recipes.Modes.Formatter, trace_levels = 0 )
    assert isinstance( truck.generalcfg.formatter_factory, base.funct.partial )
    assert isinstance( truck.printer_factory, base.funct.partial )
    debugger = truck( 0 )
    debugger( { 'key': 'value' } )
    output = simple_output.getvalue( )
    assert 'key' in output and 'value' in output
    assert '\n' in output


def test_102_produce_truck_printer_mode(
    recipes, base, vehicles, simple_output, monkeypatch
):
    ''' Truck in Printer mode uses pretty formatter and console printer. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.produce_truck(
        mode = recipes.Modes.Printer, trace_levels = 0 )
    assert (
        truck.generalcfg.formatter_factory
        == recipes.produce_pretty_formatter )
    assert isinstance( truck.printer_factory, base.funct.partial )
    debugger = truck( 0 )
    debugger( { 'key': 'value' } )
    output = simple_output.getvalue( )
    assert "'key': 'value'" in output  # Pretty-printed
    assert '\n' in output


def test_103_produce_truck_active_flavors(
    recipes, base, configuration, vehicles, simple_output, monkeypatch
):
    ''' Truck factory respects active flavors in Formatter mode. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    flavors = base.accret.Dictionary(
        info = configuration.FlavorConfiguration( ),
        error = configuration.FlavorConfiguration( ),
        debug = configuration.FlavorConfiguration( ) )
    truck = recipes.produce_truck(
        flavors = flavors,
        active_flavors = { 'info', 'error' },
        mode = recipes.Modes.Formatter )
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
    assert "Debug message" not in output


def test_200_install_truck_default(
    recipes, vehicles, simple_output, clean_builtins, monkeypatch
):
    ''' Basic installation with default alias in Formatter mode. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.install( trace_levels = 0 )
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
    ''' Installation respects trace levels in Printer mode. '''
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.install( trace_levels = 1, mode = recipes.Modes.Printer )
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


def test_300_register_module(
    recipes, configuration, vehicles,
    simple_output, clean_builtins, monkeypatch,
):
    monkeypatch.setattr( sys, 'stderr', simple_output )
    truck = recipes.install( trace_levels = 0, active_flavors = { 'debug' } )
    recipes.register_module(
        prefix_emitter = 'Rich| ',
        flavors = { 'debug': configuration.FlavorConfiguration( ) } )
    debugger = truck( 'debug' )
    debugger( { 'key': 'value' } )
    output = simple_output.getvalue( )
    assert "Rich| {'key': 'value'}" in output
