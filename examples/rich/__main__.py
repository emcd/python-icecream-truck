# ruff: noqa: F821

from typing_extensions import Any

import ictruck.recipes.rich as ictruckr


def main( ):
    ictruckr.install( trace_levels = 3, stderr = True )
    response: dict[ str, Any ] = {
        'status': 'success',
        'data': [
            { 'id': 1, 'name': 'Item 1', 'price': 9.99 },
            { 'id': 2, 'name': 'Item 2', 'price': 14.50 },
            { 'id': 3, 'name': 'Item 3', 'price': 20.25 },
        ],
        'metadata': { 'timestamp': '2025-03-20T10:00:00Z', 'version': '1.0' },
    }
    ictr( 3 )( response )


if '__main__' == __name__: main( )
