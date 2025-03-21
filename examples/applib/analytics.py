# ruff: noqa: F821


from typing_extensions import Any

from ictruck import register_module, FlavorConfiguration

# Register module with custom flavors.
register_module(
    flavors = {
        'info': FlavorConfiguration( prefix_emitter = "ANALYTICS INFO| " ),
        'error': FlavorConfiguration( prefix_emitter = "ANALYTICS ERROR| " ),
        'perf': FlavorConfiguration( prefix_emitter = "ANALYTICS PERF| " ) } )


def calculate_metrics( dataset: list[ int ] ) -> dict[ str, Any ]:
    ''' Calculates statistical metrics from dataset. '''
    ictr( 'info' )( "Calculating metrics..." )

    if not dataset:
        ictr( 'error' )( "Empty dataset provided." )
        return { }

    try:
        count = len( dataset )
        total = sum( dataset )
        average = total / count
        minimum = min( dataset )
        maximum = max( dataset )
        variance = sum( ( x - average ) ** 2 for x in dataset ) / count
        std_dev = variance ** 0.5
    except Exception as exc:
        ictr( 'error' )( exc )
        return { }

    metrics: dict[ str, Any ] = {
        'count': count,
        'total': total,
        'average': average,
        'minimum': minimum,
        'maximum': maximum,
        'variance': variance,
        'std_dev': std_dev,
    }

    ictr( 'info' )( "Metrics calculation complete." )
    ictr( 'perf' )( count )
    return metrics


def detect_anomalies(
    dataset: list[ int ], threshold = 2.0
) -> list[ tuple[ int, int, float ] ]:
    ''' Detects anomalies in dataset using standard deviation. '''
    ictr( 'info' )( f"Detecting anomalies with threshold {threshold}." )

    if not dataset:
        ictr( 'error' )( "Empty dataset provided." )
        return [ ]

    metrics = calculate_metrics( dataset )
    if not metrics: return [ ]

    anomalies: list[ tuple[ int, int, float ] ] = [ ]
    for i, value in enumerate( dataset ):
        z_score = abs( value - metrics[ 'average' ] ) / metrics[ 'std_dev' ]
        if z_score > threshold:
            anomalies.append( ( i, value, z_score ) )

    ictr( 'perf' )( len( anomalies ) )
    return anomalies
