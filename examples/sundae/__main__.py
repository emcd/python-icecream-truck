# ruff: noqa: F821,PLR2004,TRY003,TRY301

import random
import time

from typing_extensions import Any

import ictruck

from ictruck.recipes import sundae


class TaskError( Exception ):
    ''' Custom exception for task failures. '''


def main( ) -> None:
    ''' Runs task scheduler with sundae debugging. '''
    # Register the module with sundae-specific flavors.
    sundae.register_module(
        prefix_label_as = sundae.PrefixLabelPresentation.Emoji,
        prefix_template = '{timestamp} [{module_qname}] {flavor} ',
        prefix_ts_format = '%H:%M:%S' )
    # Install the truck with active flavors for this module.
    ictruck.install(
        active_flavors = {
            __name__: [ 'note', 'monition', 'error', 'success', 'abortx' ] } )
    run_scheduler( )


def run_scheduler( ) -> None:
    ''' Simulates task scheduler processing jobs. '''
    tasks: list[ dict[ str, Any ] ] = [
        { 'id': 1, 'name': 'Backup Database', 'delay': 1 },
        { 'id': 2, 'name': 'Send Emails', 'delay': 0.5 },
        { 'id': 3, 'name': 'Process Payments', 'delay': 2 },
    ]
    status = 'starting scheduler'
    ictr( 0 )( status )
    ictr( 'note' )( 'loaded tasks' )
    ictr( 1 )( tasks )
    try:
        for task in tasks:
            processing = "task #{id}: '{name}'".format( **task )
            ictr( 2 )( processing )
            result = process_task( task )
            ictr( 'success' )( result )
    finally:
        status = 'stopping scheduler'
        ictr( 0 )( status )


def process_task( task: dict[ str, Any ] ) -> dict[ str, Any ]:
    ''' Simulates task processing with potential failures. '''
    time.sleep( task[ 'delay' ] ) # Simulate work
    outcome = random.random( ) # noqa: S311
    if outcome < 0.2: # 20% chance of failure
        try: raise TaskError( 'task failed unexpectedly' )
        except TaskError as exc:
            message = 'critical error'
            ictr( 'abortx' )( message )
            raise SystemExit( 1 ) from exc
    elif outcome < 0.4: # 20% chance of partial success
        message = 'minor issues'
        ictr( 'monition' )( message, task )
        return { 'status': 'warning', 'task_id': task[ 'id' ] }
    return { 'status': 'success', 'task_id': task[ 'id' ] }


if __name__ == '__main__': main( )
