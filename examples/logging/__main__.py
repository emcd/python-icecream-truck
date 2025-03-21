# ruff: noqa: F821

import logging

import ictruck.recipes.logging as ictruckl


def main( ) -> None:
    logging.basicConfig(
        level = logging.INFO, format = '%(levelname)s: %(message)s' )
    ictruckl.install( )
    monitor_files( [ 'data1.txt', 'data2.txt' ] )


def monitor_files( files: list[ str ] ) -> None:
    import os
    ictr( 'info' )( 'Scanning', files )
    for file in files:
        ictr( 'debug' )( 'Checking', file )
        if not os.path.exists( file ):
            ictr( 'warning' )( 'Missing', file )


if __name__ == '__main__': main( )
