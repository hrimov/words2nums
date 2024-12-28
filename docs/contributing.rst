Contributing
============

We love your input! We want to make contributing to words2nums as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

Development Process
-------------------

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from ``main``.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

Pull Request Process
--------------------

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the docs/ with details of changes to the API, if applicable.
3. The PR will be merged once you have the sign-off of at least one other developer.

Development Setup
-----------------

1. Clone your fork:

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

Running Tests
-------------

Run the full test suite:

.. code-block:: bash

   pytest

Run tests with coverage:

.. code-block:: bash

   pytest --cov=words2nums

Code Style
----------

We use several tools to maintain code quality:

- ``ruff`` for linting and formatting
- ``mypy`` for type checking

Before submitting a PR, ensure your code passes all checks:

.. code-block:: bash

   # Run linting
   ruff check
   
   # Run type checking
   mypy .

Any Issues?
-----------

Feel free to file an issue if you:

- Can't get the development environment set up
- Found a bug
- Have a feature request
- Need help with something 