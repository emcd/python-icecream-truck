.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


Environments
===============================================================================

Choosing between development, testing, and production environments via
environment variables.

(Example courtesy of Anthropic claude-3-7-sonnet.)

.. literalinclude:: ../../../examples/environments/__main__.py
   :language: python

Running this will result in the following (or something similar)::

    TRACE0| 'Application starting'
    TRACE1| 'Loading configuration'
    API| method: 'GET', endpoint: '/api/config'
    API| f"API call successful": 'API call successful'
    TRACE2| 'Initializing database connections'
    DATABASE| query: 'SELECT version()'
    TRACE3| 'Establishing connection pool'
    TRACE3| 'Preparing statement'
    DATABASE| 'Query executed successfully'
    TRACE3| 'Detailed initialization steps'
    API| 'API subsystem initialized'
    DATABASE| 'Database connections established'
    AUTH| 'Authentication service ready'
    ERROR| 'This error message should appear even in production'
    TRACE1| 'Processing user operation.'
    AUTH| 'Verifying user credentials'
    CACHE| 'Checking cache for data'
    TRACE2| 'Creating user context.'
    TRACE2| 'Validating input data.'
    ERROR| 'Invalid user input detected.'
    UI| 'Updating user interface.'
    NOTICE| 'User operation completed.'
    TRACE0| 'Application shutting down'

Running this with ``APP_ENV`` set to ``testing`` will result in the following
(or something similar)::

    TRACE0| 'Application starting'
    TRACE1| 'Loading configuration'
    API| method: 'GET', endpoint: '/api/config'
    API| f"API call successful": 'API call successful'
    TRACE2| 'Initializing database connections'
    DATABASE| query: 'SELECT version()'
    DATABASE| 'Query executed successfully'
    API| 'API subsystem initialized'
    DATABASE| 'Database connections established'
    AUTH| 'Authentication service ready'
    ERROR| 'This error message should appear even in production'
    TRACE1| 'Processing user operation.'
    AUTH| 'Verifying user credentials'
    TRACE2| 'Creating user context.'
    TRACE2| 'Validating input data.'
    ERROR| 'Invalid user input detected.'
    TRACE0| 'Application shutting down'

And, running this with ``APP_ENV`` set to ``prod`` will result in the following
(or something similar)::

    TRACE0| 'Application starting'
    ERROR| 'This error message should appear even in production'
    TRACE0| 'Application shutting down'
