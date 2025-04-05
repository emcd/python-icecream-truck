#!/usr/bin/env python

# ruff: noqa: F821


import functools
import operator

import ictruck


def main( ):
    # Add 'ictr' to Python builtins.
    ictruck.install( )

    # Indicate that tracing has been enabled.
    # If we had simply done 'ictruck.install( )', it would be inactive,
    # since the default trace depth is -1.
    ictr( 0 )( "Icecream tracing active." )

    some_work( )


def some_work( ):
    answer = deeper_work( ( 2, 3, 7 ), operator.mul )
    # Can use a deeper trace level to indicate depth in call stack.
    ictr( 1 )( answer )


def deeper_work( data, operator ):
    ictr( 2 )( operator )
    for datum in data:
        # Can use a deeper trace level to indicate loop bodies.
        ictr( 3 )( datum )
    return functools.reduce( operator, data )


if '__main__' == __name__: main( )
