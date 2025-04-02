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


''' Tests for sundae recipes module. '''

# pylint: disable=unused-argument,too-many-arguments,too-many-locals
# pylint: disable=unnecessary-lambda


import sys
import time

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
    ''' Provides sundae recipes module. '''
    return cache_import_module( f"{PACKAGE_NAME}.recipes.sundae" )


@pytest.fixture( scope = 'session' )
def vehicles( ):
    ''' Provides vehicles module. '''
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


# Flavor Specifications and Aliases
def test_010_flavor_specifications( recipes ):
    ''' Verify flavor specifications are correctly defined. '''
    specs = recipes._flavor_specifications
    assert set( specs.keys() ) == {
        'note', 'monition', 'error', 'errorx',
        'abort', 'abortx', 'future', 'success' }
    assert specs['note'].color == 'blue'
    assert specs['note'].emoji == '\N{Information Source}\ufe0f'
    assert specs['note'].label == 'NOTE'
    assert not specs['note'].stack
    assert specs['errorx'].color == 'red'
    assert specs['errorx'].emoji == '❌'
    assert specs['errorx'].label == 'ERROR'
    assert specs['errorx'].stack
    assert specs['abortx'].color == 'bright_red'
    assert specs['abortx'].emoji == '💥'
    assert specs['abortx'].label == 'ABORT'
    assert specs['abortx'].stack


def test_011_flavor_aliases( recipes ):
    ''' Verify flavor aliases map correctly. '''
    aliases = recipes._flavor_aliases
    assert aliases == {
        'n': 'note', 'm': 'monition',
        'e': 'error', 'a': 'abort',
        'ex': 'errorx', 'ax': 'abortx',
        'f': 'future', 's': 'success' }


# Prefix Emission


@pytest.mark.parametrize( "decoration_name,flavor,expected_prefix", [
    ( "Plain", 'note', 'NOTE| ' ),
    ( "Color", 'note', 'NOTE| ' ),
    ( "Emoji", 'note', '\N{Information Source}\ufe0f| ' ),
    ( "Color|Emoji", 'note', '\N{Information Source}\ufe0f| ' ),
    ( "Plain", 'errorx', 'ERROR| ' ),
    ( "Color", 'errorx', 'ERROR| ' ),
    ( "Emoji", 'errorx', '❌| ' ),
    ( "Color|Emoji", 'errorx', '❌| ' ),
] )
def test_020_prefix_decorations(
    recipes, vehicles, base,
    simple_output, decoration_name, flavor, expected_prefix,
):
    ''' Test prefix decorations for special flavors. '''
    if '|' in decoration_name:
        # Handle combined decorations like "Color|Emoji"
        decoration = recipes.PrefixDecorations(0)  # Start with 0 (Plain)
        for name in decoration_name.split('|'):
            decoration |= getattr( recipes.PrefixDecorations, name )
    else:
        decoration = getattr( recipes.PrefixDecorations, decoration_name )
    console = Console( file = simple_output )
    prefix_control = recipes.PrefixFormatControl( decorations = decoration )
    emitter = recipes._produce_prefix_emitter( console, prefix_control )
    prefix = emitter( 'test_module', flavor )
    assert prefix == expected_prefix


def test_021_prefix_template_interpolants(
    recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
):
    ''' Test all prefix template interpolants. '''
    printer_factory = base.funct.partial(
        vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install(
        active_flavors = { 'note' }, printer_factory = printer_factory )
    monkeypatch.setattr(
        time, 'strftime', lambda fmt: '2025-04-01 12:00:00.000000' )
    monkeypatch.setattr( 'os.getpid', lambda: 1234 )
    monkeypatch.setattr(
        'threading.current_thread',
        lambda: type('Thread', (), {'ident': 5678, 'name': 'MainThread'})() )
    template = (
        "{timestamp} [{module_qname}] {flavor} "
        "(pid:{process_id}, tid:{thread_id}, tname:{thread_name})| " )
    recipes.register_module(
        prefix_template = template,
        prefix_decorations = recipes.PrefixDecorations.Plain )
    debugger = truck( 'note' )
    debugger( "Test message" )
    output = simple_output.getvalue()
    assert output.startswith(
        f"2025-04-01 12:00:00.000000 [{__name__}] "
        "NOTE (pid:1234, tid:5678, tname:MainThread)| " )


# def test_022_prefix_styles(
#     recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
# ):
#     ''' Test custom prefix styles for interpolants. '''
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     styles = base.AccretiveDictionary( {
#         'timestamp': Style( color = 'green' ),
#         'module_qname': Style( color = 'yellow' ),
#     } )
#     template = "{timestamp} [{module_qname}] {flavor}| "
#     monkeypatch.setattr( time, 'strftime', lambda fmt: '2025-04-01 12:00:00' )
#     recipes.register_module(
#         prefix_template = template,
#         prefix_styles = styles,
#         prefix_decorations = recipes.PrefixDecorations.Color )
#     debugger = truck( 'note' )
#     debugger( "Test message" )
#     output = simple_output.getvalue()
#     assert output.startswith( "[green]2025-04-01 12:00:00[/green] [[yellow]__main__[/yellow]] [blue]NOTE[/blue]| " )


def test_023_prefix_ts_format(
    recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
):
    ''' Test custom timestamp format in prefix. '''
    printer_factory = base.funct.partial(
        vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install(
        active_flavors = { 'note' }, printer_factory = printer_factory )
    template = "{timestamp} {flavor}| "
    monkeypatch.setattr(
        time, 'strftime',
        lambda fmt:
            '12:00:00' if fmt == '%H:%M:%S' else '2025-04-01 12:00:00' )
    recipes.register_module(
        prefix_template = template,
        prefix_ts_format = '%H:%M:%S',
        prefix_decorations = recipes.PrefixDecorations.Plain )
    debugger = truck( 'note' )
    debugger( "Test message" )
    output = simple_output.getvalue()
    assert output.startswith( "12:00:00 NOTE| " )


# Formatter Factory
def test_030_formatter_output( recipes, configuration, simple_output ):
    ''' Test formatter output with rich formatting. '''
    console = Console( file = simple_output, force_terminal = True )
    formatter = recipes._produce_formatter_factory( console )(
        configuration.FormatterControl(), 'test', 'note' )
    value = { 'key': 'value' }
    result = formatter( value )
    assert 'key' in result and 'value' in result
    assert '\n' in result  # Rich formatting includes newlines


# def test_031_formatter_stack_trace( recipes, configuration, simple_output, monkeypatch ):
#     ''' Test stack trace inclusion for errorx/abortx. '''
#     console = Console( file = simple_output, force_terminal = True )
#     formatter = recipes._produce_formatter_factory( console )(
#         configuration.FormatterControl(), 'test', 'errorx' )
#     # Simulate an active exception
#     try:
#         raise ValueError( "Test error" )
#     except ValueError:
#         exc_info = sys.exc_info()
#     monkeypatch.setattr( sys, 'exc_info', lambda: exc_info )
#     result = formatter( "Error message" )
#     assert "Error message" in result
#     assert "ValueError: Test error" in result
#     assert "Traceback" in result
#     # Test without stack trace for non-stack flavor
#     formatter = recipes._produce_formatter_factory( console )(
#         configuration.FormatterControl(), 'test', 'note' )
#     result = formatter( "Note message" )
#     assert "Note message" in result
#     assert "Traceback" not in result


def test_032_formatter_no_exception(
    recipes, configuration, simple_output, monkeypatch
):
    ''' Test formatter with no active exception for errorx/abortx. '''
    console = Console( file = simple_output, force_terminal = True )
    formatter = recipes._produce_formatter_factory( console )(
        configuration.FormatterControl(), 'test', 'errorx' )
    monkeypatch.setattr( sys, 'exc_info', lambda: (None, None, None) )
    result = formatter( "Error message" )
    assert "Error message" in result
    assert "Traceback" not in result


# # Trace Levels
# @pytest.mark.parametrize( "level,expected_color", [
#     (0, 'grey85'), (1, 'grey82'), (2, 'grey78'), (3, 'grey74'), (4, 'grey70'),
#     (5, 'grey66'), (6, 'grey62'), (7, 'grey58'), (8, 'grey54'), (9, 'grey50'),
# ] )
# def test_040_trace_prefixes( recipes, vehicles, base, simple_output, level, expected_color, monkeypatch ):
#     ''' Test trace prefixes for levels 0-9. '''
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( trace_levels = 10, printer_factory = printer_factory )
#     recipes.register_module( prefix_decorations = recipes.PrefixDecorations.Color )
#     debugger = truck( level )
#     debugger( "Trace message" )
#     output = simple_output.getvalue()
#     expected_indent = '  ' * level
#     assert output.startswith( f"[{expected_color}]TRACE{level}[/{expected_color}]| {expected_indent}" )


def test_041_trace_prefix_emoji(
    recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
):
    ''' Test trace prefix with emoji decoration. '''
    printer_factory = base.funct.partial(
        vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install(
        trace_levels = 1, printer_factory = printer_factory )
    recipes.register_module(
        prefix_decorations = recipes.PrefixDecorations.Emoji )
    debugger = truck( 0 )
    debugger( "Trace message" )
    output = simple_output.getvalue()
    assert output.startswith( "🔎| " )


# Integration
def test_100_register_module(
    recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
):
    ''' Test register_module integration with vehicles. '''
    printer_factory = base.funct.partial(
        vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install(
        active_flavors = { 'note' }, printer_factory = printer_factory )
    recipes.register_module(
        prefix_decorations = recipes.PrefixDecorations.Plain )
    debugger = truck( 'note' )
    debugger( "Integration test" )
    output = simple_output.getvalue()
    assert output == "NOTE| Integration test\n\n"


# Edge Cases


# def test_200_invalid_prefix_template(
#     recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
# ):
#     ''' Test invalid prefix template raises exception. '''
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     with pytest.raises( KeyError ):
#         recipes.register_module( prefix_template = "{invalid_key}| " )


# def test_201_invalid_ts_format(
#     recipes, vehicles, base, simple_output, clean_builtins, monkeypatch
# ):
#     ''' Test invalid timestamp format raises exception. '''
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     with pytest.raises( ValueError ):
#         recipes.register_module( prefix_template = "{timestamp}| ", prefix_ts_format = '%Q' )  # Invalid strftime format
