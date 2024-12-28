Installation
============

words2nums can be installed using pip:

.. code-block:: bash

   pip install words2nums

Requirements
------------

* Python 3.11 or higher

Development Installation
------------------------

To install words2nums for development:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/hrimov/words2nums.git
      cd words2nums

2. Create a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

3. Install dependencies:

   .. code-block:: bash

      # For development (linting and testing)
      pip install -e ".[lint,test]"
      
      # For documentation generation
      pip install -e ".[docs]"

Verification
------------

To verify the installation:

.. code-block:: python

   from words2nums import Converter
   
   converter = Converter()
   result = converter.convert("forty-two")
   assert result == 42
   
   # Test decimal numbers
   result = converter.convert("forty-two point five")
   assert result == 42.5
   
   print("Installation successful!") 