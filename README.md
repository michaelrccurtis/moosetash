# Moosetash

## A Mustache template renderer for Python

Moosetash is a python implementation of the [Mustache](https://mustache.github.io/) templating specification.

## Usage

### Basic Usage

Parsing templates is as easy as passing a template and a variable context to Moosetash's render function:

```python
from moosetash import render


render('Hello {{ variable }}!', {'variable': 'world'})
# Output: Hello world!

```

### Custom Serialisation

By default, variables are serialised through string conversion by calling `str`. This behaviour can be customised by passing your own serialisation function:

```python
from typing import Any
from datetime import date
from moosetash import render


def date_serializer(value: Any) -> str:
    if isinstance(value, date):
        return value.strftime('%d/%m/%Y')
    return str(value)


render('{{variable}}', {'variable': date(2020, 1, 10)}, serializer=date_serializer)
# Output: '10-01/2020'
```

### Fallback behaviour

By default, Mustache specifies that missing variables or partials are represented as empty strings. You can customise how the renderer handles missing variables or partials.

```python

from moosetash import (
    render,
    missing_variable_raise,
    missing_variable_keep,
)


render('{{missing}}', {})
# Output: ''

render('{{missing}}', {}, missing_variable_handler=missing_variable_raise)
# Raises: moosetash.MissingVariable('missing')

render('{{missing}}', {}, missing_variable_handler=missing_variable_keep)
# Output: '{{missing}}'

def custom_missing_handler(variable_name: str, variable_tag: str) -> str:
    return f'[Missing variable with name {variable_name}]'

render('{{missing}}', {}, missing_variable_handler=custom_missing_handler)
# Output: '[Missing variable with name missing]'

```

Similarly, for partials:

```python
from moosetash import (
    render,
    missing_partial_raise,
    missing_partial_keep,
)


render('{{>missing}}', {})
# Output: ''

render('{{>missing}}', {}, missing_partial_handler=missing_partial_raise)
# Raises: moosetash.MissingPartial('missing')

render('{{>missing}}', {}, missing_partial_handler=missing_partial_keep)
# Output: '{{missing}}'

def custom_missing_handler(partial_name: str, partial_tag: str) -> str:
    return f'[Missing partial with name {partial_name}]'

render('{{>missing}}', {}, missing_partial_handler=custom_missing_handler)
# Output: '[Missing partial with name missing]'

```

## Contributing

We welcome any contributions to this repo.

### Set up locally

Moostash uses [poetry](https://python-poetry.org/) for package management. You can install locally:

```
poetry init
```

### Tests

Moostash uses pytest for tests, and aims for 100% coverage. To run all tests with coverage output:

```
poetry run pytest --cov=moosetash
```

A significant number of tests are loaded directly from the mustache spec (see the `spec` folder.)

### Formatting

Moostash uses [black](https://github.com/psf/black) and [isort](https://pycqa.github.io/isort/) for automated formatting. Both of these should be run through poetry, and are configured in `pyproject.toml`:

```
poetry run black .
poetry run isort .
```

### Typing

Moosetash is a typed python library, and aims for comprehensive type coverage. You can check the types using [mypy](https://mypy.readthedocs.io/en/stable/):

```
poetry run mypy .
```

### Benchmarks

This repo contains a series of benchmarks that can be run against different other Python mustache renderers, for comparing performance:

-   [Chevron](https://github.com/noahmorrison/chevron) is currently the recommended Python implementation, and is generally fast and efficient.

You can run the benchmark suite using poetry:

```
poetry run benchmark
```

### TODO

-   Support for inheritance
-   Additional benchmarks
-   Performance analysis and improvement

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
