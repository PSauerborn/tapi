# Tapi: No-Code REST API Generation

`tapi` is a python CLI that generates REST APIs from standard python functions. No code changes required! Simply define the API in YAML format with a path to the python handler(s), and run using `tapi` CLI.

Powered by `FastAPI` and `uvicorn`, `tapi` handles all the tedious tasks associated with generating REST interfaces. As long as functions are annotated with valid python types, `tapi` auto-generates `pydantic` request and response models on the fly to properly handle input and output validation. Full integration with `pydantic` is also supported for complex response and request models.

### Installation

`tapi` can be installed from PyPI using `pip install pytapi`. Alternatively, `tapi` is set up using `poetry`. To install from source, just clone the repository and install with `poetry install`. Verify that the installation has been successful using `python -m tapi --help`

### Example Usage

Define some functions in standard python. `tapi` does not enforce and interface, and doesn't require any imports or bespoke code. However, function arguments and return types need to be annotated in order for `tapi` to generate the required data models.

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

Then, create a new `tapi.yml` file defining the endpoints that the REST service has. Python functions are mapped to endpoints via the `handler` field.

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

Note that the value provided for the `handler` field must be importable from the current context. Endpoints can be either `GET` or `POST` endpoints (more support for HTTP methods coming soon).

Finally, start the service using `python -m tapi run`. This will spin up a new `FastAPI` instance with `uvicorn` that can be accessed at `http://localhost:8080`. To explore the REST interface and endpoints, access the OpenAPI UI at `http://localhost:8080/docs`

#### How are function arguments handled in `tapi`?

Function arguments are handled differently depending on the endpoint type. Endpoints that are defined as `GET` endpoints require function arguments to be provided as query string parameters. If an endpoint is defined as a `POST` endpoint, `tapi` generates a `pydantic` data model at runtime that is used for the `POST` request body.

In the above example, the `execute_subtraction` function can be executed with a request to

`GET - http://localhost:8080/subtract?x=10&y=5`

The `execute_addition` endpoint on the other hand is executed with a request to

`POST - http://localhost:8080/add`

with request body

```json
{
    "x": 10,
    "y": 5
}
```

Make sure to include the `Content-Type: application/json` header for all `POST` requests.


### Supported Types

`tapi` generates a REST interface, and all inputs and outputs are converted from/into JSON. This means that any provided values need to be JSON serializable. While `tapi` does not enforce an interface, it does place some limitations on the types of values that can be returned. Currently, the only allowed types are

```python
ALLOWED_TYPES = [
    UUID,
    datetime,
    date,
    bool,
    str,
    float,
    int,
    dict,
    list,
    Dict,
    List,
    Literal,
]
```

All other annotations will raise an exception when run with `tapi`. Note that any nested combination of the above is also valid i.e. both `List` and `List[Dict[str, int]]` are allowed types.
