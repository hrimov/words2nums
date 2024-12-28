Usage Guide
===========

Basic Usage
------------

The simplest way to use words2nums is through the ``Converter`` class:

.. code-block:: python

   from words2nums import Converter
   from words2nums.core.converter import Locale

   # Create converter with default locale (English)
   converter = Converter()

   # Or specify locale explicitly
   converter = Converter(locale=Locale.ENGLISH)  # Using enum
   converter = Converter(locale="en")            # Using string

   # Cardinal numbers
   print(converter.convert("twenty-three"))  # Output: 23
   print(converter.convert("one hundred and five"))  # Output: 105

   # Ordinal numbers
   print(converter.convert("twenty-first"))  # Output: 21
   print(converter.convert("one hundred and first"))  # Output: 101
   print(converter.convert("thousandth"))  # Output: 1000

   # Decimal numbers
   print(converter.convert("twenty-three point five"))  # Output: 23.5
   print(converter.convert("one point two five"))  # Output: 1.25

   # Complex expressions
   print(converter.convert("one million two hundred thousand"))  # Output: 1200000
   print(converter.convert("two hundred and twenty-third"))  # Output: 223

Locale Support
--------------

Currently, words2nums supports the English locale, which is the default. You can specify the locale in two ways:

1. Using the ``Locale`` enum:

   .. code-block:: python

      from words2nums import Converter
      from words2nums.core.converter import Locale

      converter = Converter(locale=Locale.ENGLISH)

2. Using a string identifier:

   .. code-block:: python

      from words2nums import Converter

      converter = Converter(locale="en")

If no locale is specified, English is used by default:

.. code-block:: python

   converter = Converter()  # Uses English locale

Supported Number Formats
------------------------

words2nums supports various number formats:

* Cardinal numbers (one, two, three, ...)
* Ordinal numbers (first, second, third, ...)
* Compound numbers (twenty-one, ninety-nine, ...)
* Large numbers (thousand, million, billion, ...)
* Decimal numbers (one point five, twenty-three point four, ...)
* Complex expressions (one hundred and twenty-three, ...)

Examples:

.. code-block:: python

   converter = Converter()

   # Cardinal numbers
   converter.convert("five")  # 5
   converter.convert("forty")  # 40
   converter.convert("one hundred")  # 100

   # Ordinal numbers
   converter.convert("first")  # 1
   converter.convert("twenty-first")  # 21
   converter.convert("hundredth")  # 100
   converter.convert("one hundred first")  # 101
   converter.convert("one thousandth")  # 1000
   converter.convert("millionth")  # 1000000

   # Compound numbers
   converter.convert("twenty-one")  # 21
   converter.convert("ninety-nine")  # 99
   converter.convert("twenty-third")  # 23

   # Large numbers
   converter.convert("one thousand")  # 1000
   converter.convert("one million")  # 1000000
   converter.convert("two million first")  # 2000001

   # Decimal numbers
   converter.convert("one point five")  # 1.5
   converter.convert("twenty point zero five")  # 20.05
   converter.convert("twenty-third point one")  # 23.1

   # Complex expressions
   converter.convert("one hundred and twenty-three")  # 123
   converter.convert("one million two hundred thousand")  # 1200000
   converter.convert("two hundred and twenty-third")  # 223

Error Handling
---------------

words2nums provides clear error messages when it encounters invalid input:

.. code-block:: python

   converter = Converter()

   try:
       converter.convert("invalid input")
   except Exception as e:
       print(f"Error: {e}")

   try:
       converter.convert("twenty-three-four")  # Invalid format
   except Exception as e:
       print(f"Error: {e}")

Best Practices
---------------

1. Input Validation
   
   Always validate user input before passing it to the converter:

   .. code-block:: python

       def process_number(text):
           text = text.lower().strip()
           converter = Converter()
           try:
               return converter.convert(text)
           except Exception as e:
               print(f"Could not convert '{text}': {e}")
               return None

2. Error Handling

   Implement proper error handling to gracefully handle conversion failures:

   .. code-block:: python

       def safe_convert(text):
           converter = Converter()
           try:
               return converter.convert(text)
           except Exception:
               return None 