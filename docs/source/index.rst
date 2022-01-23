Welcome to the Safe URL Checker documentation!
==============================================

Safe URL Checker is a web service designed to efficiently check if a URL is safe to visit.

It does this by searching several databases of URLs known to contain malware.

The target use case is for serving responses to a proxy, but it could be extended to other applications.

It is easily extensible and configurable, and able to sit behind various front ends
and can access many databases. Depending on development status, some development may be required.

If you are interested in more advanced configuration, other deployment options, or development, please visit
the github repo at https://github.com/lhossack/safe_url_checker.


Deployment Quickstart
=====================
Project is not deployable yet :(


Installation
============
Please see README.md for current installation instructions for developers.
#TODO Once the service is packaged this section will be filled out for users.


Configuration
=============



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
    - It allows 1 thread to be open for write and many simultaneous readers.

        - The readers do not get updates until they reload the file.

This class should be able to use any dbm driver with no reloading. If you're 
implementing reloading please ensure there are tests particularly for 
handling reloading of dbm.gnu with multiple threads. All readers will need 
to close before the writer can be opened to update the database.

.. automodule:: urlchecker.dbm_adaptor
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
