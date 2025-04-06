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


''' Common imports and type aliases used throughout the package. '''

# ruff: noqa: F401


from __future__ import annotations

import collections.abc as   cabc
import contextlib as        ctxl
import dataclasses as       dcls
import                      enum
import functools as         funct
import                      inspect
import                      io
import itertools as         itert
import                      locale
import                      os
import                      re
import                      sys
import threading as         threads
import                      time
import                      types
import                      warnings

import typing_extensions as typx
# --- BEGIN: Injected by Copier ---
# --- END: Injected by Copier ---

from absence import Absential, absent, is_absent
from accretive.qaliases import AccretiveDictionary
from frigid.qaliases import (
    ImmutableClass,
    ImmutableCompleteDataclass,
    ImmutableDictionary,
    immutable,
    reclassify_modules_as_immutable,
)


H = typx.TypeVar( 'H', bound = cabc.Hashable ) # Hash Key
V = typx.TypeVar( 'V' ) # Value


ComparisonResult: typx.TypeAlias = bool | types.NotImplementedType
DictionaryNominativeArgument: typx.TypeAlias = typx.Annotated[
    V,
    typx.Doc(
        'Zero or more keyword arguments from which to initialize '
        'dictionary data.' ),
]
DictionaryPositionalArgument: typx.TypeAlias = typx.Annotated[
    cabc.Mapping[ H, V ] | cabc.Iterable[ tuple[ H, V ] ],
    typx.Doc(
        'Zero or more iterables from which to initialize dictionary data. '
        'Each iterable must be dictionary or sequence of key-value pairs. '
        'Duplicate keys will result in an error.' ),
]
ExceptionInfo: typx.TypeAlias = tuple[
    type[ BaseException ] | None,
    BaseException | None,
    types.TracebackType | None ]

package_name = __name__.split( '.', maxsplit = 1 )[ 0 ]
