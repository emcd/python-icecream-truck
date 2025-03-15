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


def _produce_default_flavors( ) -> __.AccretiveDictionary[ int | str, Flavor ]:
    return __.AccretiveDictionary( {
        i: Flavor( prefix = f"TRACE{i}| " ) for i in range( 10 ) } )


class Flavor(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-flavor configuration. '''
    formatter: __.typx.Annotated[
        __.typx.Optional[ Formatter ],
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
            ''' ),
    ] = None


class Module(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-module or per-package configuration. '''

    # pylint: disable=invalid-field-call
    flavors: FlavorsRegistry = ( # pyright: ignore
        __.dcls.field( default_factory = __.AccretiveDictionary ) )
    formatter: __.typx.Annotated[
        __.typx.Optional[ Formatter ],
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
            ''' ),
    ] = None
    # pylint: enable=invalid-field-call


class Vehicle(
    metaclass = __.ImmutableDataclass, # decorators = ( __.immutable, )
):
    ''' Per-vehicle configuration. '''

    # pylint: disable=invalid-field-call
    flavors: FlavorsRegistry = (
        __.dcls.field( default_factory = _produce_default_flavors ) )
    formatter: __.typx.Annotated[
        Formatter,
        __.typx.Doc( ''' Callable to convert an argument to a string. ''' ),
    ] = _icecream.DEFAULT_ARG_TO_STRING_FUNCTION
    include_context: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack frame with output? ''' )
    ] = False
    prefix: __.typx.Annotated[
        str, __.typx.Doc( ''' Prefix for output. ''' )
    ] = _icecream.DEFAULT_PREFIX
    # pylint: enable=invalid-field-call


FlavorsRegistry: __.typx.TypeAlias = (
    __.AccretiveDictionary[ int | str, Flavor ] )
# TODO? Formatter: Union with enum for Null, Pretty, Rich.
Formatter: __.typx.TypeAlias = __.typx.Callable[ [ __.typx.Any ], str ]
