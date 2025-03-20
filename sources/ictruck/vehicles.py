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
from . import configuration as _cfg
from . import exceptions as _exceptions


# pylint: disable=import-error,import-private-name
if __.typx.TYPE_CHECKING: # pragma: no cover
    import _typeshed
# pylint: enable=import-error,import-private-name


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = _exceptions.ArgumentClassInvalidity ) )


builtins_alias_default: __.typx.Annotated[
    str,
    __.typx.Doc( ''' Default alias for global truck in builtins module. ''' ),
] = 'ictr'


class Truck( metaclass = __.ImmutableCompleteDataclass ):
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
        _cfg.VehicleConfiguration,
        __.typx.Doc(
            ''' General configuration.

                Top of configuration inheritance hierarchy.
                Default is suitable for application use.
            ''' ),
    ] = __.dcls.field( default_factory = _cfg.VehicleConfiguration )
    modulecfgs: __.typx.Annotated[
        __.AccretiveDictionary[ str, _cfg.ModuleConfiguration ],
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
            tuple[ str, _cfg.Flavor ], _icecream.IceCreamDebugger ],
        __.typx.Doc(
            ''' Cache of debugger instances by module and flavor. ''' ),
    ] = __.dcls.field( default_factory = __.AccretiveDictionary ) # pyright: ignore
    _debuggers_lock: __.typx.Annotated[
        __.threads.Lock,
        __.typx.Doc( ''' Access lock for cache of debugger instances. ''' ),
    ] = __.dcls.field( default_factory = __.threads.Lock )
    # pylint: enable=invalid-field-call

    @_validate_arguments
    def __call__( self, flavor: _cfg.Flavor ) -> _icecream.IceCreamDebugger:
        ''' Vends flavor of Icecream debugger. '''
        mname = _discover_invoker_module_name( )
        cache_index = ( mname, flavor )
        if cache_index in self._debuggers: # pylint: disable=unsupported-membership-test
            with self._debuggers_lock: # pylint: disable=not-context-manager
                return self._debuggers[ cache_index ] # pylint: disable=unsubscriptable-object
        configuration = _produce_ic_configuration( self, mname, flavor )
        control = _cfg.FormatterControl( )
        initargs = _calculate_ic_initargs(
            self, configuration, control, mname, flavor )
        debugger = _icecream.IceCreamDebugger( **initargs )
        if isinstance( flavor, int ):
            trace_level = (
                _calculate_effective_trace_level( self.trace_levels, mname) )
            debugger.enabled = flavor <= trace_level
        elif isinstance( flavor, str ): # pragma: no branch
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
        configuration: __.Absential[ _cfg.ModuleConfiguration ] = __.absent,
    ) -> None:
        ''' Registers configuration for module.

            If no module or package name is given, then the current module is
            inferred.

            If no configuration is provided, then a default is generated.
        '''
        if __.is_absent( name ):
            name = _discover_invoker_module_name( )
        if __.is_absent( configuration ):
            configuration = _cfg.ModuleConfiguration( )
        self.modulecfgs[ name ] = configuration # pylint: disable=unsupported-assignment-operation


ActiveFlavors: __.typx.TypeAlias = frozenset[ _cfg.Flavor ]
ActiveFlavorsLiberal: __.typx.TypeAlias = (
    __.cabc.Sequence[ _cfg.Flavor ] | __.cabc.Set[ _cfg.Flavor ] )
ActiveFlavorsRegistry: __.typx.TypeAlias = (
    __.ImmutableDictionary[ str | None, ActiveFlavors ] )
ActiveFlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str | None, ActiveFlavorsLiberal ] )
Printer: __.typx.TypeAlias = __.cabc.Callable[ [ str ], None ]
PrinterFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, _cfg.Flavor ], Printer ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.io.TextIOBase | PrinterFactory
TraceLevelsRegistry: __.typx.TypeAlias = (
    __.ImmutableDictionary[ str | None, int ] )
TraceLevelsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str | None, int ] )

InstallAliasArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.typx.Doc(
        ''' Alias under which the truck is installed in builtins. ''' ),
]
ProduceTruckActiveFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ ActiveFlavorsLiberal | ActiveFlavorsRegistryLiberal ],
    __.typx.Doc(
        ''' Flavors to activate.

            Can be collection, which applies globally across all registered
            modules. Or, can be mapping of module names to sets.

            Module-specific entries merge with global entries.
        ''' ),
]
ProduceTruckFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.FlavorsRegistryLiberal ],
    __.typx.Doc( ''' Registry of flavor identifiers to configurations. ''' ),
]
ProduceTruckGeneralcfgArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.VehicleConfiguration ],
    __.typx.Doc(
        ''' General configuration for the truck.

            Top of configuration inheritance hierarchy. If absent,
            defaults to a suitable configuration for application use.
        ''' ),
]
ProduceTruckPrinterFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ PrinterFactoryUnion ],
    __.typx.Doc(
        ''' Factory which produces callables to output text somewhere.

            May also be writable text stream.
            Factories take two arguments, module name and flavor, and
            return a callable which takes one argument, the string
            produced by a formatter.

            If absent, uses a default.
        ''' ),
]
ProduceTruckTraceLevelsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ int | TraceLevelsRegistryLiberal ],
    __.typx.Doc(
        ''' Maximum trace depths.

            Can be an integer, which applies globally across all registered
            modules. Or, can be a mapping of module names to integers.

            Module-specific entries override global entries.
        ''' ),
]
RegisterModuleFormatterFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.FormatterFactory ],
    __.typx.Doc(
        ''' Factory which produces formatter callable.

            Takes formatter control, module name, and flavor as arguments.
            Returns formatter to convert an argument to a string.
        ''' ),
]
RegisterModuleIncludeContextArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ bool ],
    __.typx.Doc( ''' Include stack frame with output? ''' ),
]
RegisterModuleNameArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.typx.Doc(
        ''' Name of the module to register.

            If absent, infers the current module name.
        ''' ),
]
RegisterModulePrefixEmitterArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.PrefixEmitterUnion ],
    __.typx.Doc(
        ''' String or factory which produces output prefix string.

            Factory takes formatter control, module name, and flavor as
            arguments. Returns prefix string.
        ''' ),
]

@_validate_arguments
def install(
    alias: InstallAliasArgument = builtins_alias_default,
    active_flavors: ProduceTruckActiveFlavorsArgument = __.absent,
    generalcfg: ProduceTruckGeneralcfgArgument = __.absent,
    printer_factory: ProduceTruckPrinterFactoryArgument = __.absent,
    trace_levels: ProduceTruckTraceLevelsArgument = __.absent,
) -> Truck:
    ''' Installs configured truck into builtins.

        Application developers should call this early before importing
        library packages which may also use the builtin truck.

        Library developers should call :py:func:`register_module` instead.
    '''
    truck = produce_truck(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = printer_factory,
        trace_levels = trace_levels )
    __.install_builtin_safely(
        alias, truck, _exceptions.AttributeNondisplacement )
    return truck


@_validate_arguments
def produce_truck(
    active_flavors: ProduceTruckActiveFlavorsArgument = __.absent,
    generalcfg: ProduceTruckGeneralcfgArgument = __.absent,
    printer_factory: ProduceTruckPrinterFactoryArgument = __.absent,
    trace_levels: ProduceTruckTraceLevelsArgument = __.absent,
) -> Truck:
    ''' Produces icecream truck with some shorthand argument values. '''
    # TODO: Deeper validation of active flavors and trace levels.
    # TODO: Deeper validation of printer factory.
    nomargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( generalcfg ):
        nomargs[ 'generalcfg' ] = generalcfg
    if not __.is_absent( printer_factory ):
        nomargs[ 'printer_factory' ] = printer_factory
    if not __.is_absent( active_flavors ):
        if isinstance( active_flavors, ( __.cabc.Sequence,  __.cabc.Set ) ):
            nomargs[ 'active_flavors' ] = __.ImmutableDictionary(
                { None: frozenset( active_flavors ) } )
        else:
            nomargs[ 'active_flavors' ] = __.ImmutableDictionary( {
                mname: frozenset( flavors )
                for mname, flavors in active_flavors.items( ) } )
    if not __.is_absent( trace_levels ):
        if isinstance( trace_levels, int ):
            nomargs[ 'trace_levels' ] = __.ImmutableDictionary(
                { None: trace_levels } )
        else:
            nomargs[ 'trace_levels' ] = __.ImmutableDictionary( trace_levels )
    return Truck( **nomargs )


@_validate_arguments
def register_module(
    name: RegisterModuleNameArgument = __.absent,
    flavors: ProduceTruckFlavorsArgument = __.absent,
    formatter_factory: RegisterModuleFormatterFactoryArgument = __.absent,
    include_context: RegisterModuleIncludeContextArgument = __.absent,
    prefix_emitter: RegisterModulePrefixEmitterArgument = __.absent,
) -> None:
    ''' Registers module configuration on the builtin truck.

        If no truck exists in builtins, installs one which produces null
        printers.

        Intended for library developers to configure debugging flavors
        without overriding anything set by the application or other libraries.
        Application developers should call :py:func:`install` instead.
    '''
    if builtins_alias_default not in __builtins__:
        truck = Truck( printer_factory = lambda mname, flavor: lambda x: None )
        __builtins__[ builtins_alias_default ] = truck
    else: truck = __builtins__[ builtins_alias_default ]
    nomargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( flavors ):
        nomargs[ 'flavors' ] = __.ImmutableDictionary( flavors )
    if not __.is_absent( formatter_factory ):
        nomargs[ 'formatter_factory' ] = formatter_factory
    if not __.is_absent( include_context ):
        nomargs[ 'include_context' ] = include_context
    if not __.is_absent( prefix_emitter ):
        nomargs[ 'prefix_emitter' ] = prefix_emitter
    configuration = _cfg.ModuleConfiguration( **nomargs )
    truck.register_module( name = name, configuration = configuration )


def _calculate_effective_flavors(
    flavors: ActiveFlavorsRegistry, mname: str
) -> ActiveFlavors:
    result = set( flavors.get( None, frozenset( ) ) )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in flavors:
            result |= set( flavors[ mname_ ] )
    return frozenset( result )


def _calculate_effective_trace_level(
    levels: TraceLevelsRegistry, mname: str
) -> int:
    result = levels.get( None, -1 )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in levels:
            result = levels[ mname_ ]
    return result


def _calculate_ic_initargs(
    truck: Truck,
    configuration: __.ImmutableDictionary[ str, __.typx.Any ],
    control: _cfg.FormatterControl,
    mname: str,
    flavor: _cfg.Flavor,
) -> dict[ str, __.typx.Any ]:
    nomargs: dict[ str, __.typx.Any ] = { }
    nomargs[ 'argToStringFunction' ] = (
        configuration[ 'formatter_factory' ]( control, mname, flavor ) )
    nomargs[ 'includeContext' ] = configuration[ 'include_context' ]
    if isinstance( truck.printer_factory, __.io.TextIOBase ):
        printer = __.funct.partial( print, file = truck.printer_factory )
    else: printer = truck.printer_factory( mname, flavor ) # pylint: disable=not-callable
    nomargs[ 'outputFunction' ] = printer
    prefix_emitter = configuration[ 'prefix_emitter' ]
    nomargs[ 'prefix' ] = (
        prefix_emitter if isinstance( prefix_emitter, str )
        else prefix_emitter( mname, flavor ) )
    return nomargs


def _dict_from_dataclass(
    obj: _typeshed.DataclassInstance
) -> dict[ str, __.typx.Any ]:
    return {
        field.name: getattr( obj, field.name )
        for field in __.dcls.fields( obj ) }


def _discover_invoker_module_name( ) -> str:
    frame = __.inspect.currentframe( )
    while frame: # pragma: no branch
        module = __.inspect.getmodule( frame )
        if module is None:
            # pylint: disable=magic-value-comparison
            if '<stdin>' == frame.f_code.co_filename: # pragma: no cover
                name = '__main__'
                break
            # pylint: enable=magic-value-comparison
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
    for ename in ( 'formatter_factory', 'include_context', 'prefix_emitter' ):
        uvalue = update.get( ename )
        if uvalue is not None: result[ ename ] = uvalue
        elif ename in base: result[ ename ] = base[ ename ]
    return result


def _produce_ic_configuration(
    vehicle: Truck, mname: str, flavor: _cfg.Flavor
) -> __.ImmutableDictionary[ str, __.typx.Any ]:
    fconfigs: list[ _cfg.FlavorConfiguration ] = [ ]
    vconfig = vehicle.generalcfg
    configd: dict[ str, __.typx.Any ] = {
        field.name: getattr( vconfig, field.name )
        for field in __.dcls.fields( vconfig ) }
    if flavor in vconfig.flavors:
        fconfigs.append( vconfig.flavors[ flavor ] )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ not in vehicle.modulecfgs: continue
        mconfig = vehicle.modulecfgs[ mname_ ]
        configd = _merge_ic_configuration( configd, mconfig )
        if flavor in mconfig.flavors:
            fconfigs.append( mconfig.flavors[ flavor ] )
    if not fconfigs: raise _exceptions.FlavorInavailability( flavor )
    # Apply collected flavor configs after general and module configs.
    # (Applied in top-down order for correct overrides.)
    for fconfig in fconfigs:
        configd = _merge_ic_configuration( configd, fconfig )
    return __.ImmutableDictionary( configd )
