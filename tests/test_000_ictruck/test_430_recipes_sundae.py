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

# pylint: disable=line-too-long,too-many-arguments,too-many-locals
# pylint: disable=unused-argument

import pytest
from rich.style import Style

from . import PACKAGE_NAME, cache_import_module


class TestConsole:
    ''' A test-specific Console implementation that captures print calls. '''

    __test__ = False

    def __init__( self ):
        self.print_calls = []
        self.capture_texts = []  # Queue of capture texts to return

    def print( self, text, style = None, end = '\n' ):
        self.print_calls.append( ( text, style ) )

    def capture( self ):
        class CaptureContext:
            def __enter__( self ): return self
            def __exit__( self, *args ): pass
            def get( self ): return self.text
        capture = CaptureContext()
        # Pop the next capture text, or return '' if none left
        capture.text = self.capture_texts.pop( 0 ) if self.capture_texts else ''
        return capture

    def print_exception( self ):
        # Add to the queue instead of overwriting
        self.capture_texts.append( 'Mocked stack trace' )

@pytest.fixture
def test_console( ):
    ''' Provides a test-specific Console implementation. '''
    return TestConsole()

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
        time_formatter = lambda fmt: '2025-04-01 12:00:00' if fmt == '%Y-%m-%d %H:%M:%S.%f' else '12:00:00',
    )

@pytest.fixture( scope = 'session' )
def base():
    ''' Provides base utilities module. '''
    return cache_import_module( f"{PACKAGE_NAME}.__" )

@pytest.fixture( scope = 'session' )
def configuration():
    ''' Provides configuration module. '''
    return cache_import_module( f"{PACKAGE_NAME}.configuration" )

@pytest.fixture( scope = 'session' )
def recipes():
    ''' Provides sundae recipes module. '''
    return cache_import_module( f"{PACKAGE_NAME}.recipes.sundae" )

@pytest.fixture( scope = 'session' )
def vehicles():
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
        'f': 'future', 's': 'success',
    }

# Prefix Emission

@pytest.mark.parametrize( "label_as,flavor,expected_prefix,expected_style", [
    ( 'Words', 'note', 'NOTE| ', 'blue' ),
    ( 'Emoji', 'note', 'ℹ️| ', None ),
    ( 'Words|Emoji', 'note', 'ℹ️ NOTE| ', 'blue' ),
    ( 'Words', 'errorx', 'ERROR| ', 'red' ),
    ( 'Emoji', 'errorx', '❌| ', None ),
    ( 'Words|Emoji', 'errorx', '❌ ERROR| ', 'red' ),
] )
def test_020_produce_special_prefix( recipes, test_console, fake_auxiliaries, label_as, flavor, expected_prefix, expected_style ):
    ''' Test _produce_special_prefix with different label presentations. '''
    if '|' in label_as:
        presentation = recipes.PrefixLabelPresentation( 0 )
        for name in label_as.split( '|' ):
            presentation |= getattr( recipes.PrefixLabelPresentation, name )
    else: presentation = getattr( recipes.PrefixLabelPresentation, label_as )

    control = recipes.PrefixFormatControl(
        colorize = False,  # Disable colorize to avoid _stylize_interpolants overwriting interpolants
        label_as = presentation,
    )
    prefix = recipes._produce_special_prefix( test_console, fake_auxiliaries, control, 'test_module', flavor )
    assert prefix == expected_prefix
    if expected_style and control.colorize:
        label = expected_prefix.split( '|' )[0].strip()
        if ' ' in label: label = label.split( ' ' )[-1]
        assert any( call[0] == label and call[1].color == expected_style for call in test_console.print_calls )

@pytest.mark.parametrize( "label_as,level,expected_prefix,expected_style", [
    ( 'Words', 0, 'TRACE0| ', 'bright_cyan' ),
    ( 'Emoji', 0, '🔎| ', None ),
    ( 'Words|Emoji', 0, '🔎 TRACE0| ', 'bright_cyan' ),
    ( 'Words', 1, 'TRACE1|   ', 'cyan' ),
    ( 'Emoji', 1, '🔎|   ', None ),
    ( 'Words|Emoji', 1, '🔎 TRACE1|   ', 'cyan' ),
] )
def test_021_produce_trace_prefix( recipes, test_console, fake_auxiliaries, label_as, level, expected_prefix, expected_style ):
    ''' Test _produce_trace_prefix with different label presentations and levels. '''
    if '|' in label_as:
        presentation = recipes.PrefixLabelPresentation( 0 )
        for name in label_as.split( '|' ):
            presentation |= getattr( recipes.PrefixLabelPresentation, name )
    else: presentation = getattr( recipes.PrefixLabelPresentation, label_as )

    control = recipes.PrefixFormatControl(
        colorize = False,  # Disable colorize to avoid _stylize_interpolants overwriting interpolants
        label_as = presentation,
    )
    prefix = recipes._produce_trace_prefix( test_console, fake_auxiliaries, control, 'test_module', level )
    assert prefix == expected_prefix
    if expected_style and control.colorize:
        label = expected_prefix.split( '|' )[0].strip()
        if ' ' in label: label = label.split( ' ' )[-1]  # Handle "🔎 TRACE0"
        assert any( call[0] == label and call[1].color == expected_style for call in test_console.print_calls )

def test_022_stylize_interpolants( recipes, test_console ):
    ''' Test _stylize_interpolants with custom styles. '''
    interpolants = { 'timestamp': '2025-04-01', 'module_qname': 'test_module', 'flavor': 'NOTE' }
    styles = {
        'timestamp': Style( color = 'green' ),
        'module_qname': Style( color = 'yellow' ),
        'flavor': Style( color = 'blue' ),
    }
    recipes._stylize_interpolants( test_console, interpolants, styles )
    assert len( test_console.print_calls ) == 3
    assert test_console.print_calls[0] == ( '2025-04-01', styles['timestamp'] )
    assert test_console.print_calls[1] == ( 'test_module', styles['module_qname'] )
    assert test_console.print_calls[2] == ( 'NOTE', styles['flavor'] )

@pytest.mark.parametrize( "flavor,expected_prefix", [
    ( 'note', 'NOTE| ' ),
    ( 'errorx', 'ERROR| ' ),
] )
def test_023_produce_prefix_emitter_special_flavors( recipes, test_console, fake_auxiliaries, flavor, expected_prefix ):
    ''' Test _produce_prefix_emitter for special flavors. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
    )
    emitter = recipes._produce_prefix_emitter( test_console, fake_auxiliaries, control )
    prefix = emitter( 'test_module', flavor )
    assert prefix == expected_prefix

@pytest.mark.parametrize( "level,expected_prefix", [
    ( 0, 'TRACE0| ' ),
    ( 1, 'TRACE1|   ' ),
    ( 9, 'TRACE9|                   ' ),
] )
def test_024_produce_prefix_emitter_trace_levels( recipes, test_console, fake_auxiliaries, level, expected_prefix ):
    ''' Test _produce_prefix_emitter for trace levels. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
    )
    emitter = recipes._produce_prefix_emitter( test_console, fake_auxiliaries, control )
    prefix = emitter( 'test_module', level )
    assert prefix == expected_prefix

def test_025_render_prefix_interpolants( recipes, test_console, fake_auxiliaries ):
    ''' Test _render_prefix with all interpolants. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
        template = "{timestamp} [{module_qname}] {flavor} (pid:{process_id}, tid:{thread_id}, tname:{thread_name})| ",
    )
    prefix = recipes._render_prefix( test_console, fake_auxiliaries, control, 'test_module', 'NOTE', {} )
    assert prefix == "2025-04-01 12:00:00 [test_module] NOTE (pid:1234, tid:5678, tname:TestThread)| "

def test_026_render_prefix_ts_format( recipes, test_console, fake_auxiliaries ):
    ''' Test _render_prefix with custom timestamp format. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
        template = "{timestamp} {flavor}| ",
        ts_format = '%H:%M:%S',
    )
    prefix = recipes._render_prefix( test_console, fake_auxiliaries, control, 'test_module', 'NOTE', {} )
    assert prefix == "12:00:00 NOTE| "

# Formatter Factory

def test_030_formatter_output(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Test formatter output with a value. '''
    test_console.capture_texts = [ "{'key': 'value'}" ]
    formatter = recipes._produce_formatter_factory( test_console, fake_auxiliaries )(
        configuration.FormatterControl(), 'test', 'note' )
    result = formatter( { 'key': 'value' } )
    assert result == "{'key': 'value'}"

def test_031_formatter_stack_trace(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Test formatter with stack trace for errorx. '''
    # Set the capture texts in the order they will be retrieved
    test_console.capture_texts = [ "Mocked stack trace", "Error message" ]
    fake_auxiliaries = recipes.Auxiliaries(
        exc_info_discoverer = lambda: ( ValueError, ValueError( "Test error" ), None ),
        pid_discoverer = fake_auxiliaries.pid_discoverer,
        thread_discoverer = fake_auxiliaries.thread_discoverer,
        time_formatter = fake_auxiliaries.time_formatter,
    )
    formatter = recipes._produce_formatter_factory( test_console, fake_auxiliaries )(
        configuration.FormatterControl(), 'test', 'errorx' )
    result = formatter( "Error message" )
    assert result == "Mocked stack trace\nError message"

def test_032_formatter_no_stack_trace(
    recipes, configuration, test_console, fake_auxiliaries
):
    ''' Test formatter without stack trace. '''
    test_console.capture_texts = [ "Note message" ]
    formatter = recipes._produce_formatter_factory( test_console, fake_auxiliaries )(
        configuration.FormatterControl(), 'test', 'note' )
    result = formatter( "Note message" )
    assert result == "Note message"

# Integration

def test_100_register_module( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
    ''' Test register_module integration with vehicles. '''
    printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
    recipes.register_module(
        colorize = False,
        prefix_label_as = recipes.PrefixLabelPresentation.Words,
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries,
    )
    debugger = truck( 'note' )
    test_console.capture_texts = [ "Integration test" ]
    debugger( "Integration test" )
    output = simple_output.getvalue()
    assert output == "NOTE| Integration test\n"

# def test_101_register_module_colorize_default( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
#     ''' Test register_module with colorize absent, using default colorize=True. '''
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     recipes.register_module(
#         # colorize is absent, should default to True
#         prefix_label_as = recipes.PrefixLabelPresentation.Words,
#         console_factory = lambda: test_console,
#         auxiliaries = fake_auxiliaries,
#     )
#     debugger = truck( 'note' )
#     # _stylize_interpolants will call capture().get() for each interpolant:
#     # flavor="NOTE", module_qname="test_module", timestamp="2025-04-01 12:00:00",
#     # process_id="1234", thread_id="5678", thread_name="TestThread"
#     # Then debugger will call capture().get() for "Colorize test"
#     test_console.capture_texts = [
#         "NOTE", "test_module", "2025-04-01 12:00:00", "1234", "5678", "TestThread",
#         "Colorize test"
#     ]
#     debugger( "Colorize test" )
#     output = simple_output.getvalue()
#     assert output == "NOTE| Colorize test\n"
#     # Verify that styles were applied by checking print_calls
#     assert any( call[0] == 'NOTE' and call[1].color == 'blue' for call in test_console.print_calls )

def test_102_register_module_label_as_default( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
    ''' Test register_module with prefix_label_as absent, using default label_as=Words. '''
    printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
    recipes.register_module(
        colorize = False,
        # prefix_label_as is absent, should default to Words
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries,
    )
    debugger = truck( 'note' )
    test_console.capture_texts = [ "Label as default test" ]
    debugger( "Label as default test" )
    output = simple_output.getvalue()
    assert output == "NOTE| Label as default test\n"

# def test_103_register_module_custom_styles( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
#     ''' Test register_module with custom prefix_styles. '''
#     custom_styles = base.AccretiveDictionary( {
#         'flavor': Style( color = 'magenta' ),
#         'module_qname': Style( color = 'green' ),
#     } )
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     recipes.register_module(
#         colorize = True,
#         prefix_label_as = recipes.PrefixLabelPresentation.Words,
#         prefix_styles = custom_styles,
#         console_factory = lambda: test_console,
#         auxiliaries = fake_auxiliaries,
#     )
#     debugger = truck( 'note' )
#     # _stylize_interpolants will call capture().get() for each interpolant:
#     # flavor="NOTE", module_qname="test_module", timestamp="2025-04-01 12:00:00",
#     # process_id="1234", thread_id="5678", thread_name="TestThread"
#     # Then debugger will call capture().get() for "Custom styles test"
#     test_console.capture_texts = [
#         "NOTE", "test_module", "2025-04-01 12:00:00", "1234", "5678", "TestThread",
#         "Custom styles test"
#     ]
#     debugger( "Custom styles test" )
#     output = simple_output.getvalue()
#     assert output == "NOTE| Custom styles test\n"
#     # Verify custom styles were applied
#     assert any( call[0] == 'NOTE' and call[1].color == 'magenta' for call in test_console.print_calls )
#     assert any( call[0] == 'test_module' and call[1].color == 'green' for call in test_console.print_calls )

# def test_104_register_module_custom_template( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
#     ''' Test register_module with custom prefix_template. '''
#     custom_template = "[{module_qname}] {flavor} @ {timestamp} >>> "
#     printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
#     truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
#     recipes.register_module(
#         colorize = False,
#         prefix_label_as = recipes.PrefixLabelPresentation.Words,
#         prefix_template = custom_template,
#         console_factory = lambda: test_console,
#         auxiliaries = fake_auxiliaries,
#     )
#     debugger = truck( 'note' )
#     test_console.capture_texts = [ "Custom template test" ]
#     debugger( "Custom template test" )
#     output = simple_output.getvalue()
#     assert output == "[test_module] NOTE @ 2025-04-01 12:00:00 >>> Custom template test\n"

def test_105_register_module_custom_ts_format( recipes, vehicles, base, test_console, fake_auxiliaries, simple_output, clean_builtins ):
    ''' Test register_module with custom prefix_ts_format. '''
    printer_factory = base.funct.partial( vehicles.produce_simple_printer, simple_output )
    truck = vehicles.install( active_flavors = { 'note' }, printer_factory = printer_factory )
    recipes.register_module(
        colorize = False,
        prefix_label_as = recipes.PrefixLabelPresentation.Words,
        prefix_template = "{timestamp} {flavor}| ",
        prefix_ts_format = "%H:%M:%S",
        console_factory = lambda: test_console,
        auxiliaries = fake_auxiliaries,
    )
    debugger = truck( 'note' )
    test_console.capture_texts = [ "Custom ts format test" ]
    debugger( "Custom ts format test" )
    output = simple_output.getvalue()
    assert output == "12:00:00 NOTE| Custom ts format test\n"

# Edge Cases

def test_200_invalid_prefix_template( recipes, test_console, fake_auxiliaries ):
    ''' Test invalid prefix template raises exception. '''
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
        template = "{invalid_key}| ",
    )
    with pytest.raises( KeyError ):
        recipes._render_prefix( test_console, fake_auxiliaries, control, 'test_module', 'NOTE', {} )

def test_201_invalid_ts_format( recipes, test_console, fake_auxiliaries ):
    ''' Test invalid timestamp format raises exception. '''
    def raise_value_error( fmt ): raise ValueError( "Invalid format" )
    fake_auxiliaries = recipes.Auxiliaries(
        exc_info_discoverer = fake_auxiliaries.exc_info_discoverer,
        pid_discoverer = fake_auxiliaries.pid_discoverer,
        thread_discoverer = fake_auxiliaries.thread_discoverer,
        time_formatter = raise_value_error,
    )
    control = recipes.PrefixFormatControl(
        colorize = False,
        label_as = recipes.PrefixLabelPresentation.Words,
        template = "{timestamp} {flavor}| ",
        ts_format = '%Q',
    )
    with pytest.raises( ValueError ):
        recipes._render_prefix( test_console, fake_auxiliaries, control, 'test_module', 'NOTE', {} )
