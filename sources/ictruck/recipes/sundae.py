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


''' Recipe for advanced formatters.

    .. note::

        To use this module, you must have the ``rich`` package installed.
'''

# TODO? Allow selection of trace color gradients.


from __future__ import annotations

from rich.console import Console as _Console
from rich.style import Style as _Style

from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.exceptions.ArgumentClassInvalidity ) )


class FlavorSpecification( metaclass = __.ImmutableCompleteDataclass ):
    ''' Specification for custom flavor. '''

    color: __.typx.Annotated[
        str, __.typx.Doc( ''' Name of prefix color. ''' ) ]
    emoji: __.typx.Annotated[ str, __.typx.Doc( ''' Prefix emoji. ''' ) ]
    label: __.typx.Annotated[ str, __.typx.Doc( ''' Prefix label. ''' ) ]
    stack: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack trace? ''' )
    ] = False


class PrefixDecorations( __.enum.IntFlag ):
    ''' Decoration styles for prefix emission. '''

    Plain =     0
    Color =     __.enum.auto( )
    Emoji =     __.enum.auto( )


class PrefixFormatControl( metaclass = __.ImmutableCompleteDataclass ):
    ''' Format control for prefix emission. '''

    decorations: __.typx.Annotated[
        PrefixDecorations, __.typx.Doc( ''' Kinds of decoration to apply. ''' )
    ] = PrefixDecorations.Color
    styles: __.typx.Annotated[
        __.AccretiveDictionary[ str, _Style ],
        __.typx.Doc(
            ''' Mapping of interpolant names to ``rich`` style objects. ''' ),
    ] = __.AccretiveDictionary( )
    template: __.typx.Annotated[
        str,
        __.typx.Doc(
            ''' String format for prefix.

                The following interpolants are supported:
                ``flavor``: Decorated flavor.
                ``module_qname``: Qualified name of invoking module.
                ``timestamp``: Current timestamp, formatted as string.
                ``process_id``: ID of current process according to OS kernel.
                ``thread_id``: ID of current thread.
                ``thread_name``: Name of current thread.
            ''' ),
    ] = "{flavor}| " # "{timestamp} [{module_qname}] {flavor}| "
    ts_format: __.typx.Annotated[
        str,
        __.typx.Doc(
            ''' String format for prefix timestamp.

                Used by :py:func:`time.strftime`.
            ''' ),
    ] = '%Y-%m-%d %H:%M:%S.%f'


_flavor_specifications: __.ImmutableDictionary[
    str, FlavorSpecification
] = __.ImmutableDictionary(
    note = FlavorSpecification(
        color = 'blue',
        emoji = '\N{Information Source}\ufe0f',
        label = 'NOTE' ),
    monition = FlavorSpecification(
        color = 'yellow',
        emoji = '\N{Warning Sign}\ufe0f',
        label = 'MONITION' ),
    error = FlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR' ),
    errorx = FlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR', stack = True ),
    abort = FlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT' ),
    abortx = FlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT', stack = True ),
    future = FlavorSpecification(
        color = 'magenta', emoji = '🔮', label = 'FUTURE' ),
    success = FlavorSpecification(
        color = 'green', emoji = '✅', label = 'SUCCESS' ),
)

_flavor_aliases: __.ImmutableDictionary[
    str, str
] = __.ImmutableDictionary( {
    'n': 'note', 'm': 'monition',
    'e': 'error', 'a': 'abort',
    'ex': 'errorx', 'ax': 'abortx',
    'f': 'future', 's': 'success',
} )

_trace_color_names: tuple[ str, ... ] = (
    'grey85', 'grey82', 'grey78', 'grey74', 'grey70',
    'grey66', 'grey62', 'grey58', 'grey54', 'grey50' )

_trace_prefix_styles: tuple[ _Style, ... ] = tuple(
    _Style( color = name ) for name in _trace_color_names )


@_validate_arguments
def register_module(
    name: __.RegisterModuleNameArgument = __.absent,
    prefix_decorations: __.Absential[ PrefixDecorations ] = __.absent,
    prefix_styles: __.Absential[ __.cabc.Mapping[ str, _Style ] ] = __.absent,
    prefix_template: __.Absential[ str ] = __.absent,
    prefix_ts_format: __.Absential[ str ] = __.absent,
) -> None:
    ''' Register a module with sundae-specific flavor configurations. '''
    # TODO: Probe stderr and stdout for stream with TTY and use that.
    #       Longer term, we may need to rearchitect trucks so that they can
    #       provide target attributes (TTY, colorize, etc...) at runtime.
    console = _Console( stderr = True )
    prefix_fmtctl_initargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( prefix_decorations ):
        prefix_fmtctl_initargs[ 'decorations' ] = prefix_decorations
    if not __.is_absent( prefix_styles ):
        prefix_fmtctl_initargs[ 'styles' ] = prefix_styles
    if not __.is_absent( prefix_template ):
        prefix_fmtctl_initargs[ 'template' ] = prefix_template
    if not __.is_absent( prefix_ts_format ):
        prefix_fmtctl_initargs[ 'ts_format' ] = prefix_ts_format
    prefix_fmtctl = PrefixFormatControl( **prefix_fmtctl_initargs )
    flavors = _produce_flavors( console, prefix_fmtctl )
    __.register_module(
        name = name,
        flavors = flavors,
        formatter_factory = _produce_formatter_factory( console ) )


def _produce_flavors(
    console: _Console, control: PrefixFormatControl
) -> __.FlavorsRegistry:
    emitter = _produce_prefix_emitter( console, control )
    flavors: __.FlavorsRegistryLiberal = { }
    for name in _flavor_specifications.keys( ):
        flavors[ name ] = __.FlavorConfiguration( prefix_emitter = emitter )
    for alias, name in _flavor_aliases.items( ):
        flavors[ alias ] = flavors[ name ]
    for level in range( 10 ):
        flavors[ level ] = __.FlavorConfiguration( prefix_emitter = emitter )
    return __.ImmutableDictionary( flavors )


def _produce_formatter_factory( console: _Console ) -> __.FormatterFactory:

    def factory(
        control: __.FormatterControl,
        # pylint: disable=unused-argument
        mname: str,
        flavor: __.Flavor,
        # pylint: enable=unused-argument
    ) -> __.Formatter:

        def formatter( value: __.typx.Any ) -> str:
            tb_text = ''
            if isinstance( flavor, str ):
                flavor_ = _flavor_aliases.get( flavor, flavor )
                spec = _flavor_specifications[ flavor_ ]
                if spec.stack and __.sys.exc_info( )[ 0 ]:
                    with console.capture( ) as capture:
                        console.print_exception( )
                    tb_text = capture.get( )
            else: flavor_ = flavor
            with console.capture( ) as capture:
                console.print( value )
            text = capture.get( )
            if tb_text: return f"{tb_text}\n{text}"
            return text

        return formatter

    return factory


def _produce_prefix_emitter(
    console: _Console, control: PrefixFormatControl
) -> __.PrefixEmitter:

    def emitter( mname: str, flavor: __.Flavor ) -> str:
        if isinstance( flavor, int ):
            return _produce_trace_prefix( console, control, mname, flavor )
        name = _flavor_aliases.get( flavor, flavor )
        return _produce_special_prefix( console, control, mname, name )

    return emitter


def _produce_special_prefix(
    console: _Console, control: PrefixFormatControl, mname: str, flavor: str
) -> str:
    use_color = control.decorations & PrefixDecorations.Color
    use_emoji = control.decorations & PrefixDecorations.Emoji
    styles = dict( control.styles )
    spec = _flavor_specifications[ flavor ]
    if use_emoji: label = f"{spec.emoji}"
    else:
        label = f"{spec.label}"
        if use_color: styles[ 'flavor' ] = _Style( color = spec.color )
    return _render_prefix( console, control, mname, label, styles )


def _produce_trace_prefix(
    console: _Console, control: PrefixFormatControl, mname: str, level: int
) -> str:
    # TODO? Option to render indentation guides.
    use_color = control.decorations & PrefixDecorations.Color
    use_emoji = control.decorations & PrefixDecorations.Emoji
    styles = dict( control.styles )
    if use_emoji: label = '🔎'
    else:
        label = f"TRACE{level}"
        if use_color and level < len( _trace_color_names ):
            styles[ 'flavor' ] =  _Style( color = _trace_color_names[ level ] )
    indent = '  ' * level
    return _render_prefix( console, control, mname, label, styles ) + indent


def _render_prefix(
    console: _Console,
    control: PrefixFormatControl,
    mname: str,
    flavor: str,
    styles: dict[ str, _Style ],
) -> str:
    # TODO? Performance optimization: Only compute and interpolate PID, thread,
    #       and timestamp, if capabilities set permits.
    use_color = control.decorations & PrefixDecorations.Color
    thread = __.threads.current_thread( )
    interpolants: dict[ str, str ] = {
        'flavor': flavor,
        'module_qname': mname,
        'timestamp': __.time.strftime( control.ts_format ),
        'process_id': str( __.os.getpid( ) ),
        'thread_id': str( thread.ident ),
        'thread_name': thread.name,
    }
    if use_color: _stylize_interpolants( console, interpolants, styles )
    return control.template.format( **interpolants )


def _stylize_interpolants(
    console: _Console,
    interpolants: dict[ str, str ],
    styles: dict[ str, _Style ],
) -> None:
    style_default = styles.get( 'flavor' )
    interpolants_: dict[ str, str ] = { }
    for iname, ivalue in interpolants.items( ):
        style = styles.get( iname, style_default )
        if not style: continue
        with console.capture( ) as capture:
            console.print( ivalue, style = style, end = '' )
        interpolants_[ iname ] = capture.get( )
    interpolants.update( interpolants_ )
