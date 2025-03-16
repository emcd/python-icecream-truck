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


''' Configuration and fixtures for package tests. '''


import builtins
import io
import logging

import pytest
from hypothesis import settings, HealthCheck


# Configure Hypothesis to avoid slow/flaky test cases
settings.register_profile(
    'default',
    max_examples = 100,
    suppress_health_check = [
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
    ],
    deadline = None,
)
settings.load_profile( 'default' )


@pytest.fixture
def simple_output( ):
    ''' Provides a simple output capture. '''
    output = io.StringIO( )
    yield output
    output.close( )


class StructuredCapture:
    ''' Captures structured output with module and flavor information. '''

    def __init__( self ):
        self.outputs = [ ]
        self.buffer = io.StringIO( )

    def printer_factory( self, mname, flavor ):
        ''' Creates a printer that captures structured output. '''
        def printer( text ):
            self.outputs.append( ( mname, flavor, text ) )
            self.buffer.write( f"{mname}:{flavor}:{text}\n" )
        return printer

    def clear( self ):
        ''' Clears captured output. '''
        self.outputs.clear( )
        self.buffer.seek( 0 )
        self.buffer.truncate( )

    def __del__( self ):
        self.buffer.close( )


@pytest.fixture
def structured_capture( ):
    ''' Provides a structured output capture. '''
    capture = StructuredCapture( )
    yield capture
    capture.clear( )


class LogCapture( logging.Handler ):
    ''' Captures log records with full metadata. '''

    def __init__( self ):
        super( ).__init__( )
        self.records = [ ]
        self.buffer = io.StringIO( )

    def emit( self, record ):
        self.records.append( record )
        self.buffer.write(
            f"{record.levelname}:{record.name}:{record.getMessage( )}\n" )

    def clear( self ):
        ''' Clears captured log records. '''
        self.records.clear( )
        self.buffer.seek( 0 )
        self.buffer.truncate( )

    def __del__( self ):
        self.buffer.close( )


@pytest.fixture
def log_capture( ):
    ''' Provides a logging capture handler. '''
    capture = LogCapture( )
    root_logger = logging.getLogger( )
    original_level = root_logger.level
    root_logger.setLevel( logging.DEBUG )
    root_logger.addHandler( capture )
    yield capture
    root_logger.removeHandler( capture )
    root_logger.setLevel( original_level )


@pytest.fixture
def clean_builtins( ):
    ''' Preserves and restores the original builtins state. '''
    original = dict( builtins.__dict__ )
    yield
    for key in list( builtins.__dict__.keys( ) ):
        if key not in original: delattr( builtins, key )
        else: builtins.__dict__[ key ] = original[ key ]
