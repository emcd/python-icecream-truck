# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");          #
#  you may not use this file except in compliance with the License.         #
#  You may obtain a copy of the License at                                  #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#

''' Tests for sundae recipes module. '''

import re

import accretive as accret
import pytest

from rich.console import Console
from rich.style import Style

from . import PACKAGE_NAME, cache_import_module


class FakeConsole:
    ''' Fake Console implementation which captures print calls. '''

    def __init__( self ):
        import locale
        import os
        blackhole = open( # noqa: SIM115
            os.devnull, 'w', encoding = locale.getpreferredencoding( ) )
        self.console = Console( file = blackhole )
        self.print_calls = [ ]

    def print( self, text, end = '\n', highlight = None, style = None ):
        self.print_calls.append( ( text, style ) )
        self.console.print( text, style = style, end = end )

    def capture( self ): return self.console.capture( )

    def print_exception( self ):
        try: 1 / 0
        except Exception:
            self.console.print_exception( )


def _strip_ansi_c1( text ):
    # Null device is TTY on Windows. :facepalm:
    regex = re.compile( r'''\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])''' )
    return regex.sub( '', text )


@pytest.fixture
def test_console( ):
    ''' Provides a test-specific Console implementation. '''
    return FakeConsole()


@pytest.fixture
def fake_auxiliaries( recipes ):
    ''' Provides a fake Auxiliaries instance for testing. '''
    class FakeThread:
        ''' A fake thread object with ident and name attributes. '''
        def __init__( self ):
            self.ident = 5678
            self.name = 'TestThread'

    fake_thread = FakeThread()
    return recipes.Auxiliaries(
        exc_info_discoverer = lambda: ( None, None, None ),
        pid_discoverer = lambda: 1234,
        thread_discoverer = lambda: fake_thread,
        time_formatter = (
            lambda fmt:
                '2025-04-01 12:00:00'
                if fmt == '%Y-%m-%d %H:%M:%S.%f' else '12:00:00' ) )


@pytest.fixture( scope = 'session' )
def base( ):
    return cache_import_module( f"{PACKAGE_NAME}.__" )


@pytest.fixture( scope = 'session' )
def configuration( ):
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )


@pytest.fixture( scope = 'session' )
def printers( ):
    return cache_import_module( f"{PACKAGE_NAME}.printers" )


@pytest.fixture( scope = 'session' )
def recipes( ):
    return cache_import_module( f"{PACKAGE_NAME}.recipes.sundae" )


@pytest.fixture( scope = 'session' )
def vehicles():
    return cache_import_module( f"{PACKAGE_NAME}.vehicles" )


## Flavor Specifications and Aliases


def test_010_flavor_specifications( recipes ):
    ''' Flavor specifications are correctly defined. '''
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
    ''' Flavor aliases map correctly. '''
    aliases = recipes._flavor_aliases
    assert aliases == {
        'n': 'note', 'm': 'monition',
        'e': 'error', 'a': 'abort',
        'ex': 'errorx', 'ax': 'abortx',
        'f': 'future', 's': 'success',
    }


## Prefix Emission


@pytest.mark.parametrize( "label_as,flavor,expected_prefix,expected_style", [
    ( 'Words', 'note', 'NOTE| ', 'blue' ),
    ( 'Emoji', 'note', '\N{Information Source}\ufe0f| ', None ),
    ( 'Words|Emoji', 'note', '\N{Information Source}\ufe0f NOTE| ', 'blue' ),
    ( 'Words', 'errorx', 'ERROR| ', 'red' ),
    ( 'Emoji', 'errorx', '❌| ', None ),
    ( 'Words|Emoji', 'errorx', '❌ ERROR| ', 'red' ),
    ( 'Nothing', 'error', '| ', None ),
] )
def test_020_produce_special_prefix(
    recipes, test_console, fake_auxiliaries, label_as, flavor,
    expected_prefix, expected_style,
):
    ''' Special prefixes are produced with different label presentations. '''
    if '|' in label_as:
        presentation = recipes.PrefixLabelPresentations( 0 )
        for name in label_as.split( '|' ):
            presentation |= getattr( recipes.PrefixLabelPresentations, name )
    else: presentation = getattr( recipes.PrefixLabelPresentations, label_as )
    control = recipes.PrefixFormatControl(
        colorize = True, label_as = presentation )
    prefix = _strip_ansi_c1( recipes._produce_special_prefix(
        test_console, fake_auxiliaries, control, 'test_module', flavor ) )
    assert prefix == expected_prefix
    if expected_style and control.colorize:
        label = expected_prefix.split( '|' )[ 0 ].strip( )
        assert any(
            call[ 0 ] == label and call[ 1 ].color.name == expected_style
            for call in test_console.print_calls )


@pytest.mark.parametrize( "label_as,level,expected_prefix,expected_style", [
    ( 'Words', 0, 'TRACE0| ', 'grey85' ),
    ( 'Emoji', 0, '🔎| ', None ),
    ( 'Words|Emoji', 0, '🔎 TRACE0| ', 'grey85' ),
    ( 'Words', 1, 'TRACE1|   ', 'grey82' ),
    ( 'Emoji', 1, '🔎|   ', None ),
    ( 'Words|Emoji', 1, '🔎 TRACE1|   ', 'grey82' ),
    ( 'Nothing', 1, '|   ', None ),
] )
def test_021_produce_trace_prefix(
    recipes, test_console, fake_auxiliaries, label_as, level,
    expected_prefix, expected_style,
):
    ''' Level prefixes are produced with different label presentations. '''
    if '|' in label_as:
        presentation = recipes.PrefixLabelPresentations( 0 )
        for name in label_as.split( '|' ):
            presentation |= getattr( recipes.PrefixLabelPresentations, name )
    else: presentation = getattr( recipes.PrefixLabelPresentations, label_as )
    control = recipes.PrefixFormatControl(
        colorize = True, label_as = presentation )
    prefix = _strip_ansi_c1( recipes._produce_trace_prefix(
        test_console, fake_auxiliaries, control, 'test_module', level ) )
    assert prefix == expected_prefix
    if expected_style and control.colorize:
        label = expected_prefix.split( '|' )[ 0 ].strip( )
        assert any(
            call[ 0 ] == label and call[ 1 ].color.name == expected_style
            for call in test_console.print_calls )


def test_022_stylize_interpolants( recipes, test_console ):
    ''' Custom styles are applied to interpolants. '''
    interpolants = {
        'timestamp': '2025-04-01',
        'module_qname': 'test_module',
        'flavor': 'NOTE',
    }
    styles = {
        'timestamp': Style( color = 'green' ),
        'module_qname': Style( color = 'yellow' ),
        'flavor': Style( color = 'blue' ),
    }
    recipes._stylize_interpolants( test_console, interpolants, styles )
    assert len( test_console.print_calls ) == 3
    assert test_console.print_calls[ 0 ] == (
        '2025-04-01', styles['timestamp'] )
    assert test_console.print_calls[ 1 ] == (
        'test_module', styles['module_qname'] )
    assert test_console.print_calls[ 2 ] == (
        'NOTE', styles['flavor'] )


@pytest.mark.parametrize( "flavor,expected_prefix", [
    ( 'note', 'NOTE| ' ),
    ( 'errorx', 'ERROR| ' ),
] )
def test_023_produce_prefix_emitter_special_flavors(
    recipes, test_console, fake_auxiliaries, flavor, expected_prefix
):
    ''' Prefix emitters for special flavors work correctly. '''
    control = recipes.PrefixFormatControl(
        colorize = False, label_as = recipes.PrefixLabelPresentations.Words )
    emitter = recipes._produce_prefix_emitter(
        test_console, fake_auxiliaries, control )
    prefix = emitter( 'test_module', flavor )
    assert prefix == expected_prefix


@pytest.mark.parametrize( "level,expected_prefix", [
    ( 0, 'TRACE0| ' ),
    ( 1, 'TRACE1|   ' ),
    ( 9, 'TRACE9|                   ' ),
] )
def test_024_produce_prefix_emitter_trace_levels(
    recipes, test_console, fake_auxiliaries, level, expected_prefix
):
    ''' Prefix emitters for trace levels work correctly. '''
    control = recipes.PrefixFormatControl(
        colorize = False, label_as = recipes.PrefixLabelPresentations.Words )
    emitter = recipes._produce_prefix_emitter(
        test_console, fake_auxiliaries, control )
    prefix = emitter( 'test_module', level )
    assert prefix == expected_prefix


def test_025_render_prefix_interpolants(
    recipes, test_console, fake_auxiliaries
):
    ''' Prefix emitter handles all available interpolants. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentations.Words,
        template = (
            "{timestamp} [{module_qname}] {flavor} "
            "(pid:{process_id}, tid:{thread_id}, tname:{thread_name})| " ) )
    prefix = recipes._render_prefix(
        test_console, fake_auxiliaries, control, 'test_module', 'NOTE', { } )
    assert prefix == (
        "2025-04-01 12:00:00 [test_module] NOTE "
        "(pid:1234, tid:5678, tname:TestThread)| " )


def test_026_render_prefix_ts_format(
    recipes, test_console, fake_auxiliaries
):
    ''' Prefix emitter handles custom timestamp format. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentations.Words,
        template = "{timestamp} {flavor}| ",
        ts_format = '%H:%M:%S' )
    prefix = recipes._render_prefix(
        test_console, fake_auxiliaries, control, 'test_module', 'NOTE', { } )
    assert prefix == "12:00:00 NOTE| "


## Formatter Factory


def test_030_formatter_output_custom_flavor(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Formatter converts value to string. (Custom flavor.) '''
    formatter = recipes._produce_formatter_factory(
        test_console, fake_auxiliaries )(
            configuration.FormatterControl( ), 'test', 'note' )
    result = _strip_ansi_c1( formatter( { 'key': 'value' } ) )
    assert result == "{'key': 'value'}\n"


def test_031_formatter_stack_trace(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Formatter displays stack trace correctly. '''
    fake_auxiliaries = recipes.Auxiliaries(
        exc_info_discoverer = (
            lambda: ( ValueError, ValueError( "Test error" ), None ) ),
        pid_discoverer = fake_auxiliaries.pid_discoverer,
        thread_discoverer = fake_auxiliaries.thread_discoverer,
        time_formatter = fake_auxiliaries.time_formatter )
    formatter = recipes._produce_formatter_factory(
        test_console, fake_auxiliaries )(
            configuration.FormatterControl( ), 'test', 'errorx' )
    result = _strip_ansi_c1( formatter( "Error message" ) )
    assert result.endswith( "\nError message" )
    assert len( result ) > len( "\nError message" )


def test_032_formatter_output_level(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Formatter converts value to string. (Trace depth.) '''
    formatter = recipes._produce_formatter_factory(
        test_console, fake_auxiliaries )(
            configuration.FormatterControl( ), 'test', 1 )
    result = _strip_ansi_c1( formatter( { 'key': 'value' } ) )
    assert result == "{'key': 'value'}\n"


## Integration


def test_100_register_module(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins,
):
    ''' End-to-end module registration works correctly. No defaults. '''
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        colorize = False,
        prefix_label_as = recipes.PrefixLabelPresentations.Words,
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Integration test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == "NOTE| Integration test\n"


def test_101_register_module_colorize_default(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins,
):
    ''' End-to-end module registration works correctly. Colorization. '''
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        # colorize is absent, should default to True
        prefix_label_as = recipes.PrefixLabelPresentations.Words,
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Colorize test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == "NOTE| Colorize test\n"
    assert any(
        call[ 0 ] == 'NOTE' and call[ 1 ].color.name == 'blue'
        for call in test_console.print_calls )


def test_102_register_module_label_as_default(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins,
):
    ''' End-to-end module registration works correctly. Default labeling. '''
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        colorize = False,
        # prefix_label_as is absent, should default to Words
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Label as default test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == "NOTE| Label as default test\n"


def test_103_register_module_custom_styles(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins,
):
    ''' End-to-end module registration works correctly. Custom styles. '''
    custom_styles = base.accret.Dictionary( {
        # 'flavor': Style( color = 'magenta' ),
        'module_qname': Style( color = 'green' ),
    } )
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        colorize = True,
        prefix_label_as = recipes.PrefixLabelPresentations.Words,
        prefix_styles = custom_styles,
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Custom styles test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == "NOTE| Custom styles test\n"
    # assert any(
    #     call[ 0 ] == 'NOTE' and call[ 1 ].color.name == 'magenta'
    #     for call in test_console.print_calls )
    assert any(
        call[ 0 ] == __name__ and call[ 1 ].color.name == 'green'
        for call in test_console.print_calls )


def test_104_register_module_custom_template(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins,
):
    ''' End-to-end module registration works correctly. Custom template. '''
    custom_template = "[{module_qname}] {flavor} @ {timestamp} >>> "
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        colorize = False,
        prefix_label_as = recipes.PrefixLabelPresentations.Words,
        prefix_template = custom_template,
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Custom template test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == (
        f"[{__name__}] NOTE @ 2025-04-01 12:00:00 "
        '>>> "Custom template test": Custom template test\n' )


def test_105_register_module_custom_ts_format(
    recipes, vehicles, base, printers, test_console, fake_auxiliaries,
    simple_output, clean_builtins
):
    ''' End-to-end module registration works correctly. Custom timestamp. '''
    printer_factory = base.funct.partial(
        printers.produce_simple_printer, simple_output )
    truck = vehicles.produce_truck(
        modulecfgs = accret.Dictionary( ),
        active_flavors = { 'note' },
        printer_factory = printer_factory
    ).install( )
    recipes.register_module(
        colorize = False,
        prefix_label_as = recipes.PrefixLabelPresentations.Words,
        prefix_template = "{timestamp} {flavor}| ",
        prefix_ts_format = "%H:%M:%S",
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries )
    debugger = truck( 'note' )
    debugger( "Custom ts format test" )
    output = _strip_ansi_c1( simple_output.getvalue( ) )
    assert output == "12:00:00 NOTE| Custom ts format test\n"


# Edge Cases


def test_200_invalid_prefix_template(
    recipes, test_console, fake_auxiliaries
):
    ''' Invalid prefix template raises exception. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentations.Words,
        template = "{invalid_key}| " )
    with pytest.raises( KeyError ):
        recipes._render_prefix(
            test_console, fake_auxiliaries, control,
            'test_module', 'NOTE', { } )


def test_201_invalid_ts_format( recipes, test_console, fake_auxiliaries ):
    ''' Invalid timestamp format raises exception. '''
    def raise_value_error( fmt ): raise ValueError( "Invalid format" )
    fake_auxiliaries = recipes.Auxiliaries(
        exc_info_discoverer = fake_auxiliaries.exc_info_discoverer,
        pid_discoverer = fake_auxiliaries.pid_discoverer,
        thread_discoverer = fake_auxiliaries.thread_discoverer,
        time_formatter = raise_value_error,
    )
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentations.Words,
        template = "{timestamp} {flavor}| ",
        ts_format = '%Q' )
    with pytest.raises( ValueError ):
        recipes._render_prefix(
            test_console, fake_auxiliaries, control,
            'test_module', 'NOTE', { } )
