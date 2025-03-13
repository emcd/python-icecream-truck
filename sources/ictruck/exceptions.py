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


''' Family of exceptions for package API. '''


from . import __


class Omniexception(
    BaseException,
    metaclass = __.ImmutableClass,
    decorators = ( __.immutable, ),
):
    ''' Base for all exceptions raised by package API. '''
    # TODO: Class and instance attribute concealment.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class ArgumentClassInvalidity( Omnierror, TypeError ):
    ''' Argument class is invalid. '''

    def __init__( self, name: str, classes: type | tuple[ type, ... ] ):
        if isinstance( classes, type ): classes = ( classes, )
        cnames = ' | '.join( map(
            lambda cls: f"{cls.__module__}.{cls.__qualname__}", classes ) )
        super( ).__init__(
            f"Argument {name!r} must be an instance of {cnames}." )


class FlavorInavailability( Omnierror, ValueError ):
    ''' Requested flavor is not available. '''

    def __init__( self, flavor: int | str ):
        super( ).__init__( f"Flavor {flavor!r} is not available." )


class ModuleInferenceFailure( Omnierror, RuntimeError ):
    ''' Failure to infer invoking module from call stack. '''

    def __init__( self ):
        super( ).__init__( "Could not infer invoking module from call stack." )
