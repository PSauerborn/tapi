# Tapi: No-Code REST API Generation

`tapi` is a python CLI that generates REST APIs from standard python functions. No code changes required! Simply define the API in YAML format with a path to the python handler(s), and run using `tapi`.

Powered by `FastAPI` and `uvicorn`, `tapi` handles all the tedious tasks associated with generating REST interfaces. As long as functions are annotated with valid python types, `tapi` auto-generates `pydantic` request and response models on the fly to properly handle input and output validation. Full integration with `pydantic` is also supported for complex response and request models.

### Installation

`tapi` is set up using `poetry`. To install from source, clone the repository and install with `poetry install`. Verify that the installation has been successful using `python -m tapi --help`

### Example Usage

Define some functions in standard python 3

```python
def execute_addition(x: int, y: int) -> int:
    """Example handler used to execute
    simple arithmetic addition using
    two integers

    Args:
        x (int): first integer
        y (int): second integer

    Returns:
        int: integer giving result of addition
    """

    return x + y


def execute_subtraction(x: int, y: int) -> int:
    """Example handler used to execute
    simple arithmetic subtraction using
    two integers

    Args:
        x (int): first integer
        y (int): second integer

    Returns:
        int: integer giving result of subtraction
    """

    return x - y

```

Then, create a new `tapi.yml` file

```yaml
name: Example API
endpoints:
- name: addition
  path: /add
  method: POST
  handler: example.execute_addition

- name: subtraction
  path: /subtract
  method: GET
  handler: example.execute_subtraction
```

Note that the `handler` field defines a path to a python function to use as an API handler.

Finally, start the service using `python -m tapi run`. This will spin up a new `FastAPI` instance with `uvicorn` that can be accessed at `http://localhost:8080/docs`.
