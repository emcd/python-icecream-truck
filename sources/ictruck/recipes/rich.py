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

from rich.console import Console as _Console

from . import __


def produce_truck(
    install: bool = True, stderr: bool = True
) -> __.vehicles.Truck:
    ''' Produces icecream truck which is integrated with 'rich' pacakge. '''
    console = _Console( stderr = stderr )
    formatter = __.funct.partial( _console_format, console )
    generalcfg = __.configuration.Vehicle( formatter = formatter )
    target = __.sys.stderr if stderr else __.sys.stdout
    if not isinstance( target, __.io.TextIOBase ):
        # TODO: More appropriate error type.
        raise RuntimeError # noqa: TRY004
    nomargs: dict[ str, __.typx.Any ] = dict(
        generalcfg = generalcfg,
        printer_factory = __.funct.partial( _produce_simple_printer, target ) )
    if install: return __.vehicles.install( **nomargs )
    return __.vehicles.Truck( **nomargs )


# TODO: 'register_module' which adds 'pretty_repr' as formatter.


def _console_format( console: _Console, value: __.typx.Any ) -> str:
    with console.capture( ) as capture:
        console.print( value )
    return capture.get( )


def _produce_simple_printer(
    target: __.io.TextIOBase, mname: str, flavor: str # pylint: disable=unused-argument
) -> __.vehicles.Printer:
    return __.funct.partial( print, file = target )
