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


''' Recipes for Rich formatters and printers. '''


from __future__ import annotations

import colorama as _colorama
# import icecream as _icecream

from rich.console import Console as _Console

from ..configuration import (
    Flavor as _Flavor,
    Formatter as _Formatter,
    FormatterControl as _FormatterControl,
    VehicleConfiguration as _VehicleConfiguration,
)
from ..vehicles import (
    Printer as _Printer, Truck as _Truck, install as _install )
from . import __


# def install( ):


def produce_truck( install: bool = True, stderr: bool = True ) -> _Truck:
    ''' Produces icecream truck which is integrated with 'rich' pacakge. '''
    console = _Console( stderr = stderr )
    generalcfg = _VehicleConfiguration(
        formatter_factory = __.funct.partial(
            _produce_console_formatter, console ) )
    target = __.sys.stderr if stderr else __.sys.stdout
    if not isinstance( target, __.io.TextIOBase ):
        # TODO: More appropriate error type.
        raise RuntimeError # noqa: TRY004
    nomargs: dict[ str, __.typx.Any ] = dict(
        generalcfg = generalcfg,
        printer_factory = __.funct.partial( _produce_simple_printer, target ) )
    if install: return _install( **nomargs )
    return _Truck( **nomargs )


# TODO: 'register_module' which adds 'pretty_repr' as formatter.


def _console_format( console: _Console, value: __.typx.Any ) -> str:
    with console.capture( ) as capture:
        console.print( value )
    return capture.get( )


def _produce_console_formatter(
    console: _Console,
    # pylint: disable=unused-argument
    control: _FormatterControl,
    mname: str,
    flavor: int | str,
    # pylint: enable=unused-argument
) -> _Formatter:
    return __.funct.partial( _console_format, console )


# def _produce_prefix( console: _Console, mname: str, flavor: _Flavor ) -> str:
#     # TODO: Detect if terminal supports 256 colors or true color.
#     #       Make spectrum of hues for trace depths, if so.
#     return _icecream.DEFAULT_PREFIX


def _produce_simple_printer(
    target: __.io.TextIOBase,
    # pylint: disable=unused-argument
    mname: str,
    flavor: _Flavor,
    # pylint: enable=unused-argument
) -> _Printer:
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
