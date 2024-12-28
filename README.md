# words2nums

Convert word-form numbers to numerical values in Python.

[![PyPI version](https://img.shields.io/pypi/v/words2nums)](https://pypi.org/project/words2nums/)
[![Coverage](coverage.svg)](https://github.com/hrimov/words2nums/blob/main/coverage.svg)
[![Documentation Status](https://readthedocs.org/projects/words2nums/badge/?version=latest)](https://words2nums.readthedocs.io)

## Features

- Convert word-form numbers to numerical values (integers and floats)
- Support for cardinal and ordinal numbers
- Support for English language (extensible to other languages)
- Handle complex number expressions
- Clean and maintainable codebase
- Type-safe implementation
- Comprehensive test coverage

## Requirements

- Python 3.11 or higher

## Installation

```bash
pip install words2nums
```

## Quick Start

```python
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
```

## Documentation

Full documentation is available at [https://words2nums.readthedocs.io/](https://words2nums.readthedocs.io/)

## Development

1. Clone the repository:

   ```bash
   git clone https://github.com/hrimov/words2nums.git
   cd words2nums
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   # For development (linting and testing)
   pip install -e ".[lint,test]"

   # For documentation generation
   pip install -e ".[docs]"
   ```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.
