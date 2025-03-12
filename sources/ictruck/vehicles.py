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


''' Vehicles which vend flavors of Icecream debugger. '''


from __future__ import annotations

import inspect as _inspect

import icecream as _icecream

from . import __
from . import configuration as _configuration
from . import exceptions as _exceptions


class Truck(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Vends flavors of Icecream debugger. '''

    # pylint: disable=invalid-field-call
    generalcfg: __.typx.Annotated[
        _configuration.Vehicle,
        __.typx.Doc(
            ''' General instance configuration.

                Top of configuration inheritance hierarchy.
                Default is suitable for application use.
                Library developers should provide a no-op printer.
            ''' ),
    ] = __.dcls.field(
        default_factory = _configuration.Vehicle.produce_with_trace_levels )
    modulecfgs: __.typx.Annotated[
        __.AccretiveDictionary[ str, _configuration.Module ],
        __.typx.Doc(
            ''' Registry of per-module configurations.

                Modules inherit configuration from their parent packages.
                Top-level packages inherit from general instance
                configruration.
            ''' ),
    ] = __.dcls.field( default_factory = __.AccretiveDictionary ) # pyright: ignore
    # pylint: enable=invalid-field-call

    def __call__( self, flavor: int | str ) -> _icecream.IceCreamDebugger:
        ''' Vends flavor of Icecream debugger. '''
        mname = _discover_invoker_module_name( )
        # TODO? Caching of debuggers.
        configuration = _produce_ic_configuration( self, mname, flavor )
        debugger = _icecream.IceCreamDebugger(
            argToStringFunction = configuration[ 'formatter' ],
            includeContext = configuration[ 'include_context' ],
            outputFunction = configuration[ 'printer' ],
            prefix = configuration[ 'prefix' ] )
        if isinstance( flavor, int ):
            debugger.enabled = (
                flavor <= configuration.get( 'trace_level', -1 ) )
        elif isinstance( flavor, str ):
            debugger.enabled = (
                flavor in configuration.get(
                    'active_flavors', set( ) ) ) # pyright: ignore
        return debugger

    def register_module(
        self,
        name: __.Absential[ str ] = __.absent,
        configuration: __.Absential[ _configuration.Module ] = __.absent,
    ) -> None:
        ''' Registers configuration for module.

            If no module or package name is given, then the current module is
            inferred.

            If no configuration is provided, then a default is generated.
        '''
        # TODO: Runtime checks of non-absent argument types.
        if __.is_absent( name ):
            name = _discover_invoker_module_name( )
        if __.is_absent( configuration ):
            configuration = _configuration.Module( )
        self.modulecfgs[ name ] = configuration # pylint: disable=unsupported-assignment-operation


def _discover_invoker_module_name( ) -> str:
    frame = _inspect.currentframe( )
    while frame:
        module = _inspect.getmodule( frame )
        if module is None:
            if '<stdin>' == frame.f_code.co_filename: # pylint: disable=magic-value-comparison
                name = '__main__'
                break
            # TODO: Raise appropriate error.
            raise _exceptions.Omnierror(
                "Could not determine calling module." )
        name = module.__name__
        if not name.startswith( f"{__package__}." ): break
        frame = frame.f_back
    return name


def _iterate_module_name_ancestry( name: str ) -> __.cabc.Iterator[ str ]:
    parts = name.split( '.' )
    for i in range( len( parts ) ):
        yield '.'.join( parts[ : i + 1 ] )


def _merge_ic_configuration(
    base: dict[ str, __.typx.Any ], update: dict[ str, __.typx.Any ]
) -> dict[ str, __.typx.Any ]:
    result: dict[ str, __.typx.Any ] = { }
    result[ 'active_flavors' ] = (
            set( base.get( 'active_flavors', set( ) ) )
        |   set( update.get( 'active_flavors', set( ) ) ) )
    result[ 'flavors' ] = (
            dict( base.get( 'flavors', dict( ) ) )
        |   dict( update.get( 'flavors', dict( ) ) ) )
    for ename in (
        'formatter', 'include_context', 'prefix', 'printer', 'trace_level'
    ):
        uvalue = update.get( ename )
        if uvalue is not None: result[ ename ] = uvalue
        elif ename in base: result[ ename ] = base[ ename ]
    return result


def _produce_ic_configuration(
    vehicle: Truck, mname: str, flavor: int | str
) -> __.ImmutableDictionary[ str, __.typx.Any ]:
    vconfig = vehicle.generalcfg
    configd: dict[ str, __.typx.Any ] = {
        field.name: getattr( vconfig, field.name )
        for field in __.dcls.fields( vconfig ) }
    has_flavor = flavor in vconfig.flavors
    if has_flavor:
        fconfig = vconfig.flavors[ flavor ]
        configd = _merge_ic_configuration(
            configd, {
                field.name: getattr( fconfig, field.name )
                for field in __.dcls.fields( fconfig ) } )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ not in vehicle.modulecfgs: continue
        mconfig = vehicle.modulecfgs[ mname_ ]
        configd = _merge_ic_configuration(
            configd, {
                field.name: getattr( mconfig, field.name )
                for field in __.dcls.fields( mconfig ) } )
        if flavor not in mconfig.flavors: continue
        has_flavor = True
        fconfig = mconfig.flavors[ flavor ]
        configd = _merge_ic_configuration(
            configd, {
                field.name: getattr( fconfig, field.name )
                for field in __.dcls.fields( fconfig ) } )
    if not has_flavor:
        # TODO: Raise appropriate error.
        raise _exceptions.Omnierror( f"Flavor {flavor!r} does not exist." )
    return __.ImmutableDictionary( configd )
