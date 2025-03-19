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


''' Recipes for Rich formatters and printers.

    .. note::

        To use this module, you must have the ``rich`` package installed.
'''


from __future__ import annotations

import colorama as _colorama
# import icecream as _icecream

from rich.console import Console as _Console

from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.exceptions.ArgumentClassInvalidity ) )


class ConsoleTextIoInvalidity( __.exceptions.Omnierror, TypeError ):
    ''' Text stream invalid for use with Rich console. '''

    def __init__( self, stream: __.typx.Any ):
        super( ).__init__( f"Invalid stream for Rich console: {stream!r}" )


ProduceTruckStderrArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.typx.Doc( ''' Output to standard diagnostic stream? ''' )
]


@_validate_arguments
def install(
    alias: __.InstallAliasArgument = __.builtins_alias_default,
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    # TODO? Choice of truck type (console formatter | console printer ).
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    ''' Installs configured truck into builtins.

        Application developers should call this early before importing
        library packages which may also use the builtin truck.
    '''
    truck = produce_truck(
        active_flavors = active_flavors,
        trace_levels = trace_levels,
        stderr = stderr )
    __builtins__[ alias ] = truck
    return truck


@_validate_arguments
def produce_truck(
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    # TODO? Choice of truck type (console formatter | console printer ).
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    ''' Produces icecream truck which integrates with Rich. '''
    console = _Console( stderr = stderr )
    generalcfg = __.VehicleConfiguration(
        formatter_factory = __.funct.partial(
            _produce_console_formatter, console ) )
    target = __.sys.stderr if stderr else __.sys.stdout
    if not isinstance( target, __.io.TextIOBase ):
        raise ConsoleTextIoInvalidity( target )
    nomargs: dict[ str, __.typx.Any ] = dict(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = __.funct.partial( _produce_simple_printer, target ),
        trace_levels = trace_levels )
    return __.produce_truck( **nomargs )


# TODO: 'register_module' which adds 'pretty_repr' as formatter.


def _console_format( console: _Console, value: __.typx.Any ) -> str:
    with console.capture( ) as capture:
        console.print( value )
    return capture.get( )


def _produce_console_formatter(
    console: _Console,
    # pylint: disable=unused-argument
    control: __.FormatterControl,
    mname: str,
    flavor: int | str,
    # pylint: enable=unused-argument
) -> __.Formatter:
    return __.funct.partial( _console_format, console )


# def _produce_prefix( console: _Console, mname: str, flavor: _Flavor ) -> str:
#     # TODO: Detect if terminal supports 256 colors or true color.
#     #       Make spectrum of hues for trace depths, if so.
#     return _icecream.DEFAULT_PREFIX


def _produce_simple_printer(
    target: __.io.TextIOBase,
    # pylint: disable=unused-argument
    mname: str,
    flavor: __.Flavor,
    # pylint: enable=unused-argument
) -> __.Printer:
    return __.funct.partial( _simple_print, target = target )


def _simple_print( text: str, target: __.io.TextIOBase ) -> None:
    with _windows_replace_ansi_sgr( ):
        print( text, file = target )


@__.ctxl.contextmanager
def _windows_replace_ansi_sgr( ) -> __.typx.Generator[ None, None, None ]:
    # Note: Copied from the 'icecream' sources.
    #       Converts ANSI SGR sequences to Windows API calls on older
    #       command terminals which do not have proper ANSI SGR support.
    #       Otherwise, rendering on terminal occurs normally.
    _colorama.init( )
    yield
    _colorama.deinit( )
