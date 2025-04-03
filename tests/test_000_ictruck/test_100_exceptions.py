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


''' Tests for exceptions module. '''


import pytest

from . import cache_import_module


@pytest.fixture
def exceptions( ):
    ''' Provides exceptions module. '''
    return cache_import_module( 'ictruck.exceptions' )


def test_000_omniexception_base( exceptions ):
    ''' Omniexception is base for all others. '''
    assert issubclass(
        exceptions.Omnierror, exceptions.Omniexception )
    assert issubclass(
        exceptions.ArgumentClassInvalidity, exceptions.Omnierror )
    assert issubclass(
        exceptions.FlavorInavailability, exceptions.Omnierror )
    assert issubclass(
        exceptions.ModuleInferenceFailure, exceptions.Omnierror )


def test_010_argument_class_invalidity( exceptions ):
    ''' ArgumentClassInvalidity exception provides helpful message. '''
    with pytest.raises( exceptions.ArgumentClassInvalidity ) as excinfo:
        raise exceptions.ArgumentClassInvalidity( 'test_arg', str )
    assert 'test_arg' in str( excinfo.value )
    assert 'str' in str( excinfo.value )


def test_020_flavor_inavailability( exceptions ):
    ''' FlavorInavailability exception properly formats flavor. '''
    with pytest.raises( exceptions.FlavorInavailability ) as excinfo:
        raise exceptions.FlavorInavailability( 'debug' )
    assert "Flavor 'debug'" in str( excinfo.value )
    with pytest.raises( exceptions.FlavorInavailability ) as excinfo:
        raise exceptions.FlavorInavailability( 3 )
    assert "Flavor 3" in str( excinfo.value )


def test_030_module_inference_failure( exceptions ):
    ''' ModuleInferenceFailure has expected message. '''
    with pytest.raises( exceptions.ModuleInferenceFailure ) as excinfo:
        raise exceptions.ModuleInferenceFailure( )
    assert "Could not infer invoking module" in str( excinfo.value )
