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


''' Tests for printers module. '''


import pytest


from . import PACKAGE_NAME, cache_import_module


@pytest.fixture( scope = 'session' )
def printers( ):
    ''' Provides printers module. '''
    return cache_import_module( f"{PACKAGE_NAME}.printers" )


def test_010_simple_printer_output( printers, simple_output ):
    ''' Simple printer outputs text to target stream without ANSI colors. '''
    printer = printers.produce_simple_printer( simple_output, 'test', 1 )
    text_core = "Test output"
    text = f"\x1b[33m{text_core}\x1b[0m"
    printer( text )
    assert simple_output.getvalue( ) == f"{text_core}\n"


def test_011_simple_printer_color_output( printers, simple_output ):
    ''' Simple printer outputs text to target stream with ANSI colors. '''
    printer = (
        printers.produce_simple_printer(
            simple_output, 'test', 1, force_color = True ) )
    text = "\x1b[33mTest output\x1b[0m"
    printer( text )
    assert simple_output.getvalue( ) == f"{text}\n"
