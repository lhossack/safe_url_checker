Welcome to the Safe URL Checker documentation!
==============================================

Safe URL Checker is a web service designed to efficiently check if a URL is safe to visit.

It does this by searching several databases of URLs known to contain malware.

The target use case is for serving responses to a proxy, but it could be extended to other applications.

It is easily extensible and configurable, and able to sit behind various front ends
and can access many databases. Depending on development status, some development may be required.

If you are interested in more advanced configuration, other deployment options, or development, please visit
the github repo at https://github.com/lhossack/safe_url_checker.


How URLs are Checked
====================
A URL that is entered into the database may be in one of 3 forms: 

1. including just the hostname and port, e.g. `example.com:80`
2. including hostname, port and path, e.g. `example.com:443/` or `example.com:443/path/to/resource`
3. including a query string at the end, e.g. `example.com:80/path/to/res?q=something&p=specific`

In the case of option 1, all requests to that domain and port will return as hosting malware. In the case of 2, any 
requests made to that specific path (not shorter or longer) will be reported as hosting malware. In the case of 3, 
users will not be blocked if their query is even slightly different. It is this particular query that will be reported
as hosting malware.

URLs that cannot be parsed are reported as unsafe.

Currently this behaviour is not configurable. 


Deployment Quickstart
=====================
Project is not deployable yet :(


Installation
============
Please see README.md for current installation instructions for developers.
#TODO Once the service is packaged this section will be filled out for users.


Configuration
=============
Configuration is handled via a json configuration file and environment variables.

All paths provided in the configuration file must be either absolute, or relative to the configuration file.

Sample resources, including a sample configuration file and dbm.dumb databases can be found
in `sample_resources/`.

Environment Variables
---------------------

    - `URLINFO_CONFIG` defines where the config file is. There is a default configuration file in the urlchecker source directory which is used if `URLINFO_CONFIG` is not defined or can't be opened. Config file path must be either an absolute path, or a relative path from urlchecker/config_reader.py.
    - `URLINFO_LOGLEVEL` defines logging level for the server. It must be one of "INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL".


Configuration file
--------------------

An example configuration file looks like this:

.. literalinclude:: ../../sample_resources/default_config.json
  :linenos:
  :language: JSON

The global keys in the dictionary are:

- databases: a list of database configurations. There must be at least 1 database configured.

Database Configuration
^^^^^^^^^^^^^^^^^^^^^^
A database configuration consists of 2 elements (type: str and options: object).

There are some different database adaptors, and each has their own configuration options.

"dbm.dumb" databases have two options: 

- filename: string - path to database file(s)
- reload_time: int | null - time in minutes between database file reloads. If you don't want the app to reload, enter `null`.

.. code-block:: JSON

    {
        "type": "dbm.dumb",
        "options": {
            "filename": "sample1",
            "reload_time": 10
        }
    }

Note: Some configurations in the configuration file may specify that information is stored in an 
environment variable. This is useful for things like usernames/ passwords, or other items
that need to be securely stored or managed. These can be injected into docker containers 
at run time, allowing them to be stored in secure locations and rotated relatively easily.


API Documentation
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

urlchecker
----------
.. automodule:: urlchecker.urlchecker
    :members:


database_abc
------------
.. automodule:: urlchecker.database_abc
    :members:


dbm_adaptor
-----------
*Note*: This module currently uses only dbm.dumb for this adaptor. 
This means it has fairly low performance relative to dbm.gnu and dbm.ndbm.
However, it has the following benefits:

    - It is more portable across python versions and runtime environments.
    - It allows 1 thread to be open for write and many simultaneous readers. However note that the readers do not get updates until they reload the file.

This class should be able to use any dbm driver with no reloading. If you're 
implementing reloading please ensure there are tests particularly for 
handling reloading of dbm.gnu with multiple threads. All readers will need 
to close before the writer can be opened to update the database.

.. automodule:: urlchecker.dbm_adaptor
    :members:


config_reader
--------------
.. automodule:: urlchecker.config_reader
    :members:


flask_frontend
---------------
.. automodule:: urlchecker.flask_frontend
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
