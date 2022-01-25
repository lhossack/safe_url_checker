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

In the case of option 1, all requests to that domain and port will return as hosting malware. In the case of 2, any requests made to that specific path (not shorter or longer) will be reported as hosting malware. In the case of 3, users will not be blocked if their query is even slightly different. It is this particular query that will be reported as hosting malware.

Please also note that URLs are checked based on their FQDN (fully qualified domain name) if that is what is provided to the endpoint. The server does not do DNS lookups to resolve the IP, so a user who enters an IP address instead of FQDN could circumvent the system. If you wish to prevent this, either add URLs with both FQDN and all known IP addresses or patch the service.

URLs that cannot be parsed are reported as unsafe.

Currently this behaviour is not configurable. 


Deployment Quickstart
=====================
This deployment guide assumes you have docker and docker-compose installed. They are not necessary for a deployment, but these instructions will not describe non-dockerized deployments.

For installation instructions for docker and docker-compose please see: 

- https://docs.docker.com/engine/install/
- https://docs.docker.com/compose/install/

To deploy with the built-in configurations, a Dockerfile and docker-compose.yaml are provided.

If you have these tools installed, you can start up the production server by navigating the project root in a terminal and running:

```
docker-compose up
```

You can then access the endpoint at `http://localhost:8000/urlinfo/1/` from the host machine.

For example, you can try entering: 

- `http://localhost:8000/urlinfo/1/www.facebook.com:443/messages/t/62132`, or
- `http://localhost:8000/urlinfo/1/evil.com:80`

in your browser, which should yeild a "safe" and "unsafe" response respectively.

The docker image by default loads the sample_resources databases loaded. Since these are not production values, the configuration should be changed. 

To do this, you should create your own databases of urls and add them to the docker image and configuration file. While creating your own databases, keep in mind how the urls that you add will be understood by the server as described in "How URLs are Checked" above. 

A sample script "sample_resources/load_unsafe_urls.py" can help you load dbm databases from .txt files containing a malicious url on each row. Note that it doesn't enter URL fragments into the database, but the hostname:port and base path. Also note that the inputs do not contain schemas, and ports are defined after every hostname. 

Database configuration is handled via the configuration json file as described in the configuration section below.

If you create a new database, it will need to be COPY'd into the docker image along with the new configuration json file that references your database. Ensure that you update the environment variable: `URLINFO_CONFIG` in docker to point to your new configuration file. You can override it and rebuild the image 

The files that are necessary to deploy successfully are:

- urlchecker/*
- setup.py
- requirements.txt
- README.md
- at least one database and configuration file pointing to this database


Deployment - Advanced
=====================
The above deployment steps are enough to test the production server, but are likely not sufficient for production operations.

This section will discuss where to find additional information for configuring and tuning the production deployment. Please ensure you also understand the application configuration options and environment variables described in the configuration section.

Deployment to production for the flask based application uses a gunicorn server. To learn how to change the gunicorn configuration, please see https://docs.gunicorn.org/en/stable/configure.html. 

Some of the options you may be interested in include: 

- TLS configuration
- Logging
- Worker processes and threads, for tuning/ optimization
- Request limits, to prevent certain security/ availability related attacks
- Server hooks, for monitoring 

You should also look into your docker deployment environment to verify logs handling, monitoring/ alerts, etc.


Deployment Scenarios
---------------------
This docker image can safely be deployed on many nodes, perhaps behind a load balancer or proxy. DBM databases are read-only from the application, so this permits them to be copied on each node effectively creating a "read replica" for each node. This is likely not ideal unless you have data that doesn't change (or doesn't change often) and is only a small number of URLs.

The DBM databases are COPY'd into the docker image at build time. They could be externally referenced, however using bindmounts, but this will vary depending on environment. This would allow them to be modified from the host OS, and reloaded as per the configuration settings for that database.

The configuration reader does not reload configuration currently. A configuration change will require replacing the docker container.

#TODO Add section for using mongo

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
