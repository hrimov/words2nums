words2nums
=============

words2nums is a Python library that converts word-form numbers (like "twenty-three") into their numerical representation (23).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   contributing
   changelog

Features
--------

* Convert word-form numbers to integers
* Support for English language (extensible to other languages)
* Handle complex number expressions
* Clean and maintainable codebase
* Type-safe implementation
* Comprehensive test coverage

Quick Start
------------

.. code-block:: python

   from words2nums import Converter
   
   converter = Converter()
   result = converter.convert("twenty-three")
   print(result)  # Output: 23

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

