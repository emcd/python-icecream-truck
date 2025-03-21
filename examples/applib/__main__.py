# ruff: noqa: F821

import os
import sys


# Ensure that our demonstration package is available.
sys.path.insert( 0, os.path.dirname( __file__ ) )


import ictruck

# Application installs truck with both trace levels and active flavors.
# While active flavors could be global, targeting a particular package
# generally makes more sense.
#
# Installation needs to happen before module registers itself.
ictruck.install(
    trace_levels = 2,
    active_flavors = { 'analytics': [ 'info', 'error', 'perf' ] } )

from analytics import calculate_metrics, detect_anomalies # noqa: E402


def main( ):
    ictr( 0 )( "Application running." )

    normal_data = [ 10, 12, 11, 13, 10, 14, 12, 11, 10, 13 ]
    ictr( 0 )( "Calculating metrics..." )
    metrics = calculate_metrics( normal_data )
    ictr( 1 )( metrics ) # Greater depth for more detail.

    anomaly_data = [ 10, 12, 11, 13, 10, 40, 12, 11, 10, 13 ]
    ictr( 0 )( "Detecting anomalies..." )
    anomalies = detect_anomalies( anomaly_data )

    if anomalies:
        summary = f"Found {len( anomalies )} anomalies."
        ictr( 1 )( summary )
        for position, value, z_score in anomalies:
            ictr( 2 )( position, value, z_score )

    ictr( 0 )( "Calculating metrics on empty dataset..." )
    calculate_metrics( [ ] )

    ictr( 0 )( "Application finished" )


if __name__ == "__main__": main( )
