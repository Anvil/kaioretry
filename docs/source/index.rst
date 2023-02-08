.. kaioretry documentation master file, created by
   sphinx-quickstart on Tue Jan 24 22:40:02 2023.

Welcome to KaioRetry's documentation!
=====================================

KaioRetry current version is |release|

KaioRetry allows you to easily retry a function call.


Installation
------------

KaioRetry is published on pypi. You know the drill, right?


.. code:: bash

   $ pip install kaioretry


Depdendencies
-------------

At runtime, KaioRetry relies on `decorator
<https://github.com/micheles/decorator>`_ to efficiently propagate type
annotations and other metadata of the decorated function, to the function
produced by the decorator.


.. toctree::
   :maxdepth: 2
   :caption: KaioRetry:

   introduction.rst
   getting-started.rst
   decorators.rst
   kaioretry.rst
