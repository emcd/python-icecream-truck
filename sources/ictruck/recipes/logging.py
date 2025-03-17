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


''' Recipes for logging printers. '''


from __future__ import annotations

from . import __


def produce_logging_truck( install: bool = True ) -> __.vehicles.Truck:
    ''' Produces icecream truck that is integrated with 'logging' module. '''
    active_flavors = { None: frozenset( {
        'debug', 'info', 'warning', 'error', 'critical' } ) }
    flavors: __.AccretiveDictionary[ int | str, __.configuration.Flavor ] = (
        __.AccretiveDictionary(
            {   name: __.configuration.Flavor( )
                for name in active_flavors[ None ] } ) )
    generalcfg = __.configuration.Vehicle( flavors = flavors )
    nomargs = dict(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = _logger_factory )
    if install: return __.vehicles.install( **nomargs )
    return __.vehicles.Truck( **nomargs ) # pyright: ignore


def _logger_factory(
    mname: str, flavor: int | str
) -> __.cabc.Callable[ [ str ], None ]:
    import logging
    logger = logging.getLogger( mname )
    level = (
        getattr( logging, flavor.upper( ) ) if isinstance( flavor, str )
        else logging.DEBUG )
    return lambda x: logger.log( level, x )
