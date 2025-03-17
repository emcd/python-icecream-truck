#!/usr/bin/env python

import logging

import ictruck


ictruck.install( trace_levels = 3 )
ictr( 1 )( ictr ) # noqa: F821


logging.basicConfig( level = logging.INFO )
truck = ictruck.produce_logging_truck( install = False )
message = "Hello, world. Goodbye, forest."
truck( 'warning' )( message )
truck( 'info' )( truck )
