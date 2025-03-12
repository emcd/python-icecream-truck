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


''' Portions of configuration hierarchy. '''


from __future__ import annotations

import icecream as _icecream

from . import __


class Flavor(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-flavor configuration. '''
    formatter: __.typx.Annotated[
        __.typx.Optional[ __.typx.Callable[ [ __.typx.Any ], str ] ],
        __.typx.Doc(
            ''' Callable to convert an argument to a string.

                Default ``None`` inherits from module configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from module configuration.
            ''' ),
    ] = None
    prefix: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc(
            ''' Prefix for output.

                Default ``None`` inherits from module configuration.
            ''' )
    ] = None
    printer: __.typx.Annotated[
        __.typx.Optional[
            __.io.TextIOBase | __.typx.Callable[ [ str ], None ] ],
        __.typx.Doc(
            ''' Callable or stream to output text somewhere.

                Default ``None`` inherits from module configuration.

                Note: Library developers should never set this. Application
                developers decide how and where output appears.
            ''' ),
    ] = None


class Module(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-module or per-package configuration. '''

    # pylint: disable=invalid-field-call
    # TODO: Accretive set for active flavors.
    active_flavors: __.cabc.MutableSet[ int | str ] = (
        __.dcls.field( default_factory = set ) )
    flavors: __.AccretiveDictionary[ int | str, Flavor ] = ( # pyright: ignore
        __.dcls.field( default_factory = __.AccretiveDictionary ) )
    formatter: __.typx.Annotated[
        __.typx.Optional[ __.typx.Callable[ [ __.typx.Any ], str ] ],
        __.typx.Doc(
            ''' Callable to convert an argument to a string.

                Default ``None`` inherits from instance configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from instance configuration.
            ''' ),
    ] = None
    prefix: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc(
            ''' Prefix for output.

                Default ``None`` inherits from instance configuration.
            ''' )
    ] = None
    printer: __.typx.Annotated[
        __.typx.Optional[
            __.io.TextIOBase | __.typx.Callable[ [ str ], None ] ],
        __.typx.Doc(
            ''' Callable or stream to output text somewhere.

                Default ``None`` inherits from instance configuration.

                Note: Library developers should never set this. Application
                developers decide how and where output appears.
            ''' ),
    ] = None
    trace_level: __.typx.Annotated[
        int,
        __.typx.Doc(
            ''' Maximum trace depth for which to activate debuggers.

                Only applies to integer flavors and not named flavors.
            ''' ),
    ] = 9
    # pylint: enable=invalid-field-call


class Vehicle(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-vehicle configuration. '''

    # pylint: disable=invalid-field-call
    flavors: __.AccretiveDictionary[ int | str, Flavor ] = ( # pyright: ignore
        __.dcls.field( default_factory = __.AccretiveDictionary ) )
    formatter: __.typx.Annotated[
        # TODO? Union with enum for Null, Pretty, Rich.
        __.typx.Callable[ [ __.typx.Any ], str ],
        __.typx.Doc( ''' Callable to convert an argument to a string. ''' ),
    ] = _icecream.DEFAULT_ARG_TO_STRING_FUNCTION
    include_context: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack frame with output? ''' )
    ] = False
    prefix: __.typx.Annotated[
        str, __.typx.Doc( ''' Prefix for output. ''' )
    ] = _icecream.DEFAULT_PREFIX
    printer: __.typx.Annotated[
        __.io.TextIOBase | __.typx.Callable[ [ str ], None ],
        __.typx.Doc( ''' Callable or stream to output text somewhere. ''' ),
    ] = _icecream.DEFAULT_OUTPUT_FUNCTION
    # pylint: enable=invalid-field-call

    @classmethod
    def produce_with_trace_levels( # pylint: disable=too-many-arguments
        selfclass,
        # TODO: PEP 727 Doc objects for arguments.
        # pylint: disable=unused-argument
        flavors: __.Absential[
            __.cabc.Mapping[ int | str, Flavor ] ] = __.absent,
        formatter: __.Absential[
            __.typx.Callable[ [ __.typx.Any ], str ] ] = __.absent,
        include_context: __.Absential[ bool ] = __.absent,
        prefix: __.Absential[ str ] = __.absent,
        printer: __.Absential[
            __.io.TextIOBase | __.typx.Callable[ [ str ], None ],
        ] = __.absent,
        # pylint: enable=unused-argument
    ) -> __.typx.Self:
        ''' Produces instance with default set of trace depths. '''
        nomargs = { }
        for aname in ( 'formatter', 'include_context', 'prefix', 'printer' ):
            argument = locals( )[ aname ]
            if not __.is_absent( argument ):
                nomargs[ aname ] = argument
        flavors_: dict[ int | str, Flavor ] = {
            i: Flavor( prefix = f"TRACE{i}| " ) for i in range( 10 ) }
        if not __.is_absent( flavors ): flavors_.update( flavors )
        nomargs[ 'flavors' ] = flavors_
        return selfclass( **nomargs ) # pyright: ignore
