API Reference
=============

Core Module
-----------

.. py:module:: words2nums.core

The core module provides the main functionality for converting word-form numbers to numerical values.

Converter
~~~~~~~~~

.. py:class:: words2nums.Converter

   Main class for converting word-form numbers to numerical values.

   .. py:method:: convert(text: str) -> ReturnValue

      Convert a word-form number to its numerical representation.

      :param text: The word-form number to convert (e.g., "twenty-three", "one point five")
      :type text: str
      :return: The numerical representation of the word-form number
      :rtype: ReturnValue
      :raises EvaluationError: If the input text cannot be converted to a number

Components
----------

Tokenizer
~~~~~~~~~

.. py:class:: words2nums.tokenizer.Tokenizer

   Tokenizes input text into a sequence of number-related tokens.

   .. py:method:: tokenize(text: str) -> List[str]

      Convert input text into a list of tokens.

      :param text: The input text to tokenize
      :type text: str
      :return: A list of tokens
      :rtype: List[str]

Parser
~~~~~~

.. py:class:: words2nums.parser.Parser

   Parses tokenized input into a number data structure.

   .. py:method:: parse(tokens: List[str]) -> NumberData

      Parse tokens into a number data structure.

      :param tokens: List of tokens to parse
      :type tokens: List[str]
      :return: Parsed number data structure
      :rtype: NumberData

Evaluator
~~~~~~~~~

.. py:class:: words2nums.evaluator.Evaluator

   Evaluates the parsed number data to produce a numerical result.

   .. py:method:: evaluate(data: NumberData) -> ReturnValue

      Evaluate parsed number data to produce a number.

      :param data: The number data to evaluate
      :type data: NumberData
      :return: The evaluated number
      :rtype: ReturnValue
      :raises EvaluationError: If the data cannot be evaluated

Types
-----

.. py:class:: words2nums.core.types.NumberData

   Protocol defining the interface for parsed number data.

.. py:class:: words2nums.core.types.ReturnValue

   Type alias for Union[int, float], representing the possible return types.

Exceptions
----------

.. py:exception:: words2nums.exceptions.EvaluationError

   Base exception for evaluation errors.

   .. py:attribute:: message
      :type: str

      The error message.

Configuration
-------------

The library uses several configuration constants that can be customized:

.. code-block:: python

   from words2nums.constants import MAGNITUDE_LEVELS

   # Magnitude levels for number parsing
   print(MAGNITUDE_LEVELS)  # {'hundred': 2, 'thousand': 3, ...} 