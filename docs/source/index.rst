Welcome to the Safe URL Checker documentation!
==============================================

Safe URL Checker is a web service designed to efficiently check if a URL is safe to visit.

It does this by searching several databases of URLs known to contain malware.

The target use case is for serving responses to a proxy. 

It is easily extensible and configurable to sit behind various front ends
and can access many databases.

Quickstart
==========
Project is not deployable yet

Installation
============
Please see README.md for current installation instructions for developers.
Once the service is packaged this section will be filled out for users.


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

.. automodule:: urlchecker.dbm_adaptor
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
