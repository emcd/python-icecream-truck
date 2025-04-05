# ruff: noqa: F821,PLR2004


import os
import sys
import random
from enum import Enum


import ictruck


class Environment( Enum ):
    DEV = 'development'
    TEST = 'testing'
    PROD = 'production'


def main( ):
    env_name = os.environ.get( 'APP_ENV', 'development' ).lower( )
    try: env = next( ev for ev in Environment if ev.value == env_name )
    except StopIteration:
        print(
            f"Warning: Unknown environment '{env_name}', "
            "defaulting to development", file = sys.stderr )
        env = Environment.DEV

    flavors: dict[ ictruck.Flavor, ictruck.FlavorConfiguration ] = {
        'api': ictruck.FlavorConfiguration( prefix_emitter = 'API| ' ),
        'db': ictruck.FlavorConfiguration( prefix_emitter = 'DATABASE| ' ),
        'auth': ictruck.FlavorConfiguration( prefix_emitter = 'AUTH| ' ),
        'cache': ictruck.FlavorConfiguration( prefix_emitter = 'CACHE| ' ),
        'ui': ictruck.FlavorConfiguration( prefix_emitter = 'UI| ' ),
        'error': ictruck.FlavorConfiguration( prefix_emitter = 'ERROR| ' ),
        'warning': ictruck.FlavorConfiguration( prefix_emitter = 'WARNING| ' ),
        'notice': ictruck.FlavorConfiguration( prefix_emitter = 'NOTICE| ' ),
        **ictruck.produce_default_flavors( ),
    }

    trace_levels = -1  # Default to disabled
    active_flavors = [ ]

    match env:
        case Environment.DEV:
            # Development: Full debugging
            trace_levels = 9  # All trace levels
            active_flavors = [
                'api', 'db', 'auth', 'cache', 'ui',
                'error', 'warning', 'notice' ]
        case Environment.TEST:
            # Testing: Moderate debugging
            trace_levels = 2  # Only important traces
            active_flavors = [ 'api', 'db', 'auth', 'error', 'warning' ]
        case Environment.PROD:
            # Production: Minimal debugging (errors only)
            trace_levels = 0  # Only critical traces
            active_flavors = [ 'error' ]

    # Allow trace levels to be overridden by environment variable
    if 'DEBUG_LEVEL' in os.environ:
        try: trace_levels = int( os.environ[ 'DEBUG_LEVEL' ] )
        except ValueError:
            print(
                f"Warning: Invalid DEBUG_LEVEL '{os.environ['DEBUG_LEVEL']}', "
                "using default", file = sys.stderr )
    # Allow active flavors to be overridden by environment variable
    if 'DEBUG_FLAVORS' in os.environ:
        override_flavors = [
            f.strip( ) for f in os.environ[ 'DEBUG_FLAVORS' ].split( "," ) ]
        # Only use flavors that are registered
        active_flavors = [ f for f in override_flavors if f in flavors ]

    generalcfg = ictruck.VehicleConfiguration( flavors = flavors )
    ictruck.install(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        trace_levels = trace_levels )

    run_application( )


def run_application( ):
    ''' Simulates application with various debug outputs. '''
    ictr( 0 )( "Application starting" )
    # API calls (level 1 trace)
    ictr( 1 )( "Loading configuration" )
    api_call( "/api/config", "GET" )
    # Database operations (level 2 trace)
    ictr( 2 )( "Initializing database connections" )
    db_query( "SELECT version()" )
    # Detailed operations (level 3 trace)
    ictr( 3 )( "Detailed initialization steps" )
    # Named flavors for specific subsystems
    ictr( 'api' )( "API subsystem initialized" )
    ictr( 'db' )( "Database connections established" )
    ictr( 'auth' )( "Authentication service ready" )
    # Always show error messages
    ictr( 'error' )( "This error message should appear even in production" )
    # Simulate a user operation with multiple debug levels
    process_user_operation( )
    # Application shutdown
    ictr( 0 )( "Application shutting down" )


def api_call( endpoint, method, data = None ):
    ''' Simulates API call with debug tracking. '''
    ictr( 'api' )( method, endpoint )
    # Simulate success/failure
    if random.random( ) < 0.9: # noqa: S311
        ictr( 'api' )( "API call successful" )
        return { 'status': 'success' }
    ictr( 'warning' )( "API call failed" )
    return { 'status': 'error' }


def db_query( query ):
    ''' Simulates database query with debug tracking. '''
    ictr( 'db' )( query )
    ictr( 3 )( "Establishing connection pool" )
    ictr( 3 )( "Preparing statement" )
    # Success/failure simulation
    if random.random( ) < 0.95: # noqa: S311
        ictr( 'db' )( "Query executed successfully" )
        return [ { 'result': 'Sample data' } ]
    ictr( 'error' )( "Database query failed" )
    return None


def process_user_operation( ):
    ''' Simulates user operation with various debug outputs. '''
    ictr( 1 )( "Processing user operation." )
    ictr( 'auth' )( "Verifying user credentials" )
    ictr( 'cache' )( "Checking cache for data" )
    ictr( 2 )( "Creating user context." )
    ictr( 2 )( "Validating input data." )
    # Simulate error condition
    if random.random( ) < 0.2: # noqa: S311
        ictr( 'error' )( "Invalid user input detected." )
    ictr( 'ui' )( "Updating user interface." )
    ictr( 'notice' )( "User operation completed." )


if __name__ == '__main__': main( )
