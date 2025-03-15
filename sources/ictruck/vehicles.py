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

import icecream as _icecream

from . import __
from . import configuration as _configuration
from . import exceptions as _exceptions


if __.typx.TYPE_CHECKING:
    import _typeshed # pylint: disable=import-error,import-private-name


_builtins_alias_default = 'ictr'


def _validate_arguments( function: __.cabc.Callable[ ..., __.typx.Any ] ):

    @__.funct.wraps( function )
    def validate( *posargs: __.typx.Any, **nomargs: __.typx.Any ):
        ''' Validates arguments before invocation. '''
        signature = __.inspect.signature( function )
        inspectee = signature.bind( *posargs, **nomargs )
        inspectee.apply_defaults( )
        for name, value in inspectee.arguments.items( ):
            param = signature.parameters[ name ]
            annotation = param.annotation
            if __.is_absent( value ): continue
            if annotation is param.empty: continue
            classes = _reduce_annotation( annotation )
            if not isinstance( value, classes ):
                raise _exceptions.ArgumentClassInvalidity( name, classes )
        return function( *posargs, **nomargs )

    return validate


class Truck(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Vends flavors of Icecream debugger. '''

    # pylint: disable=invalid-field-call
    active_flavors: __.typx.Annotated[
        ActiveFlavorsRegistry,
        __.typx.Doc(
            ''' Mapping of module names to active flavor sets.

                Key ``None`` applies globally. Module-specific entries
                override globals for that module.
            ''' ),
    ] = __.dcls.field( default_factory = __.ImmutableDictionary ) # pyright: ignore
    generalcfg: __.typx.Annotated[
        _configuration.Vehicle,
        __.typx.Doc(
            ''' General configuration.

                Top of configuration inheritance hierarchy.
                Default is suitable for application use.
            ''' ),
    ] = __.dcls.field( default_factory = _configuration.Vehicle )
    modulecfgs: __.typx.Annotated[
        __.AccretiveDictionary[ str, _configuration.Module ],
        __.typx.Doc(
            ''' Registry of per-module configurations.

                Modules inherit configuration from their parent packages.
                Top-level packages inherit from general instance
                configruration.
            ''' ),
    ] = __.dcls.field( default_factory = __.AccretiveDictionary ) # pyright: ignore
    printer_factory: __.typx.Annotated[
        PrinterFactoryUnion,
        __.typx.Doc(
            ''' Factory which produces callables to output text somewhere.

                May also be writable text stream.
                Factories take two arguments, module name and flavor, and
                return a callable which takes one argument, the string
                produced by a formatter.
            ''' ),
    ] = __.dcls.field(
        default_factory = (
            lambda: lambda mname, flavor: _icecream.DEFAULT_OUTPUT_FUNCTION ) )
    trace_levels: __.typx.Annotated[
        TraceLevelsRegistry,
        __.typx.Doc(
            ''' Mapping of module names to maximum trace depths.

                Key ``None`` applies globally. Module-specific entries
                override globals for that module.
            ''' ),
    ] = __.dcls.field(
        default_factory = lambda: __.ImmutableDictionary( { None: -1 } ) )
    _debuggers: __.typx.Annotated[
        __.AccretiveDictionary[
            tuple[ str, int | str ], _icecream.IceCreamDebugger ],
        __.typx.Doc(
            ''' Cache of debugger instances by module and flavor. ''' ),
    ] = __.dcls.field( default_factory = __.AccretiveDictionary ) # pyright: ignore
    _debuggers_lock: __.typx.Annotated[
        __.threads.Lock,
        __.typx.Doc( ''' Access lock for cache of debugger instances. ''' ),
    ] = __.dcls.field( default_factory = __.threads.Lock )
    # pylint: enable=invalid-field-call

    @_validate_arguments
    def __call__( self, flavor: int | str ) -> _icecream.IceCreamDebugger:
        ''' Vends flavor of Icecream debugger. '''
        mname = _discover_invoker_module_name( )
        cache_index = ( mname, flavor )
        if cache_index in self._debuggers: # pylint: disable=unsupported-membership-test
            with self._debuggers_lock: # pylint: disable=not-context-manager
                return self._debuggers[ cache_index ] # pylint: disable=unsubscriptable-object
        configuration = _produce_ic_configuration( self, mname, flavor )
        if isinstance( self.printer_factory, __.io.TextIOBase ):
            printer = __.funct.partial( print, file = self.printer_factory )
        else: printer = self.printer_factory( mname, flavor ) # pylint: disable=not-callable
        debugger = _icecream.IceCreamDebugger(
            argToStringFunction = configuration[ 'formatter' ],
            includeContext = configuration[ 'include_context' ],
            outputFunction = printer,
            prefix = configuration[ 'prefix' ] )
        if isinstance( flavor, int ):
            trace_level = (
                _calculate_effective_trace_level( self.trace_levels, mname) )
            debugger.enabled = flavor <= trace_level
        elif isinstance( flavor, str ):
            active_flavors = (
                _calculate_effective_flavors( self.active_flavors, mname ) )
            debugger.enabled = flavor in active_flavors
        with self._debuggers_lock: # pylint: disable=not-context-manager
            self._debuggers[ cache_index ] = debugger # pylint: disable=unsupported-assignment-operation
        return debugger

    @_validate_arguments
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
        if __.is_absent( name ):
            name = _discover_invoker_module_name( )
        if __.is_absent( configuration ):
            configuration = _configuration.Module( )
        self.modulecfgs[ name ] = configuration # pylint: disable=unsupported-assignment-operation


ActiveFlavorsRegistry: __.typx.TypeAlias = (
    __.cabc.Mapping[ str | None, __.cabc.Set[ int | str ] ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.typx.Union[
    __.io.TextIOBase,
    __.cabc.Callable[ [ str, int | str ], __.cabc.Callable[ [ str ], None ] ],
]
TraceLevelsRegistry: __.typx.TypeAlias = __.cabc.Mapping[ str | None, int ]


@_validate_arguments
def install(
    alias: str = _builtins_alias_default,
    active_flavors: __.Absential[
        __.cabc.Set[ int | str ] | ActiveFlavorsRegistry ] = __.absent,
    generalcfg: __.Absential[ _configuration.Vehicle ] = __.absent,
    printer_factory: __.Absential[ PrinterFactoryUnion ] = __.absent,
    trace_levels: __.Absential[ int | TraceLevelsRegistry ] = __.absent,
) -> Truck:
    ''' Installs configured truck into builtins.

        Application developers should call this early before importing
        library packages which may also use the builtin truck.

        Library developers should call :py:func:`register_module` instead.
    '''
    # TODO: Deeper validation of active flavors and trace levels.
    # TODO: Deeper validation of printer factory.
    nomargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( generalcfg ):
        nomargs[ 'generalcfg' ] = generalcfg
    if not __.is_absent( printer_factory ):
        nomargs[ 'printer_factory' ] = printer_factory
    if not __.is_absent( active_flavors ):
        if isinstance( active_flavors, __.cabc.Set ):
            nomargs[ 'active_flavors' ] = __.ImmutableDictionary(
                { None: set( active_flavors ) } )
        else:
            nomargs[ 'active_flavors' ] = __.ImmutableDictionary( {
                mname: set( flavors )
                for mname, flavors in active_flavors.items( ) } )
    if not __.is_absent( trace_levels ):
        if isinstance( trace_levels, int ):
            nomargs[ 'trace_levels' ] = __.ImmutableDictionary(
                { None: trace_levels } )
        else:
            nomargs[ 'trace_levels' ] = __.ImmutableDictionary( trace_levels )
    truck = Truck( **nomargs )
    __builtins__[ alias ] = truck
    return truck


@_validate_arguments
def register_module(
    name: __.Absential[ str ] = __.absent,
    configuration: __.Absential[ _configuration.Module ] = __.absent,
) -> None:
    ''' Registers module configuration on the builtin truck.

        If no truck exists in builtins, installs one which produces null
        printers.

        Intended for library developers to configure debugging flavors
        without overriding anything set by the application or other libraries.
        Application developers should call :py:func:`install` instead.
    '''
    if _builtins_alias_default not in __builtins__:
        truck = Truck( printer_factory = lambda mname, flavor: lambda x: None )
        __builtins__[ _builtins_alias_default ] = truck
    else: truck = __builtins__[ _builtins_alias_default ]
    truck.register_module( name = name, configuration = configuration )


def _calculate_effective_flavors(
    flavors: __.cabc.Mapping[ str | None, __.cabc.Set[ int | str ] ],
    mname: str,
) -> __.cabc.Set[ int | str ]:
    result = set( flavors.get( None, set( ) ) )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in flavors:
            result |= flavors[ mname_ ]
    return result


def _calculate_effective_trace_level(
    levels: __.cabc.Mapping[ str | None, int ],
    mname: str,
) -> int:
    result = levels.get( None, -1 )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in levels:
            result = levels[ mname_ ]
    return result


def _dict_from_dataclass(
    obj: _typeshed.DataclassInstance
) -> dict[ str, __.typx.Any ]:
    return {
        field.name: getattr( obj, field.name )
        for field in __.dcls.fields( obj ) }


def _discover_invoker_module_name( ) -> str:
    frame = __.inspect.currentframe( )
    while frame:
        module = __.inspect.getmodule( frame )
        if module is None:
            if '<stdin>' == frame.f_code.co_filename: # pylint: disable=magic-value-comparison
                name = '__main__'
                break
            raise _exceptions.ModuleInferenceFailure
        name = module.__name__
        if not name.startswith( f"{__package__}." ): break
        frame = frame.f_back
    return name


def _iterate_module_name_ancestry( name: str ) -> __.cabc.Iterator[ str ]:
    parts = name.split( '.' )
    for i in range( len( parts ) ):
        yield '.'.join( parts[ : i + 1 ] )


def _merge_ic_configuration(
    base: dict[ str, __.typx.Any ], update_obj: _typeshed.DataclassInstance
) -> dict[ str, __.typx.Any ]:
    update: dict[ str, __.typx.Any ] = _dict_from_dataclass( update_obj )
    result: dict[ str, __.typx.Any ] = { }
    result[ 'flavors' ] = (
            dict( base.get( 'flavors', dict( ) ) )
        |   dict( update.get( 'flavors', dict( ) ) ) )
    for ename in ( 'formatter', 'include_context', 'prefix' ):
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
        configd = _merge_ic_configuration( configd, fconfig )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ not in vehicle.modulecfgs: continue
        mconfig = vehicle.modulecfgs[ mname_ ]
        configd = _merge_ic_configuration( configd, mconfig )
        if flavor not in mconfig.flavors: continue
        has_flavor = True
        fconfig = mconfig.flavors[ flavor ]
        configd = _merge_ic_configuration( configd, fconfig )
    if not has_flavor: raise _exceptions.FlavorInavailability( flavor )
    return __.ImmutableDictionary( configd )


# pylint: disable=eval-used
def _reduce_annotation( annotation: __.typx.Any ) -> tuple[ type, ... ]:
    origin = __.typx.get_origin( annotation )
    if origin is None:
        obj = (
            eval( annotation ) if isinstance( annotation, str ) # nosec: B307
            else annotation )
        if isinstance( obj, __.types.UnionType ):
            return tuple( __.itert.chain.from_iterable(
                map( _reduce_annotation, __.typx.get_args( obj ) ) ) )
        return ( obj, )
    if origin is __.typx.Annotated:
        return _reduce_annotation( annotation.__origin__ )
    if origin is __.typx.Union:
        return tuple( __.itert.chain.from_iterable(
            map( _reduce_annotation, __.typx.get_args( origin ) ) ) )
    # TODO? Other special forms.
    return ( origin, )
# pylint: enable=eval-used
