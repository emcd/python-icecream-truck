#!/usr/bin/env python

# ruff: noqa: F821
# ruff: noqa: F401, F841


import functools as funct
import sys

import icecream
import ictruck

from rich.pretty import pretty_repr
from rich.console import Console


def main( ):
    icecream.install( )
    console = Console( stderr = True )
    formatter = funct.partial( _format, console )
    printer = funct.partial( print, file = sys.stderr )
    # ic.configureOutput(
    #     argToStringFunction = formatter, outputFunction = printer )
    ic.configureOutput(
        argToStringFunction = pretty_repr, outputFunction = console.print )
    # ic( sys.modules )
    ic( icecream.__dict__ )


def _format( console, value ):
    with console.capture( ) as capture:
        console.print( value )
    return capture.get( )


if '__main__' == __name__: main( )
