import logging
from typing import Callable
from enum import Enum

from rich import print
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from tapi.api.logic import (
    generate_input_model,
    generate_output_model,
    replace_function_signature,
)
from tapi.api.constants import ENDPOINT_META, BASE_META


LOGGER = logging.getLogger("tapi.api")


class APIMethod(str, Enum):

    GET = "GET"
    POST = "POST"


def generate_get_endpoint(handler: Callable, name: str) -> Callable:
    """Function used to generate GET endpoint
    from a python function

    Args:
        handler (Callable): _description_

    Returns:
        Callable: _description_
    """

    response_model = generate_output_model(handler, name)

    async def api_handler(*args, **kwargs) -> response_model:
        result = handler(*args, **kwargs)
        content = {"http_code": status.HTTP_200_OK, "result": result}
        return JSONResponse(content=content)

    # replace doc string to ensure that descriptions
    # are propagated
    api_handler.__doc__ = handler.__doc__
    api_handler.__name__ = handler.__name__
    # replace function signature
    api_handler = replace_function_signature(handler, api_handler)
    return api_handler, response_model


def generate_post_endpoint(handler: Callable, name: str) -> Callable:
    """Function used to generate POST endpoint
    from a given python function

    Args:
        handler (Callable): _description_

    Returns:
        Callable: _description_
    """

    request_body_model = generate_input_model(handler, name)
    response_model = generate_output_model(handler, name)

    async def api_handler(r: request_body_model) -> response_model:
        # evaluate target function and generate response
        result = handler(**r.dict())
        content = {"http_code": status.HTTP_200_OK, "result": result}
        return JSONResponse(content=content)

    # replace doc string to ensure that descriptions
    # are propagated
    api_handler.__doc__ = handler.__doc__
    api_handler.__name__ = handler.__name__

    return api_handler, response_model


async def global_exception_handler(request, exc):
    """Global exception handler that ensures
    that any non-http exceptions that are
    uncaught in code are converted to 500
    JSON responses"""

    content = {
        "http_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "Internal server error",
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


async def http_exception_handler(request, exc):
    """Exception handler used to convert all
    HTTPExceptions into unified JSON format"""

    content = {"http_code": exc.status_code, "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=content)


async def health_check_handler() -> JSONResponse:
    """API handlers used to serve health
    check response.
    Returns
    -------
    JSONResponse
        JSON response containing success message
    """

    content = {"http_code": status.HTTP_200_OK, "message": "Service is running"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


class TapiBaseAPI(FastAPI):
    """API containing base functionality"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add exception handler to convert instance
        # of unhandled exceptions into JSON format
        self.exception_handler(Exception)(global_exception_handler)
        self.exception_handler(StarletteHTTPException)(http_exception_handler)

        self.get("/health_check", **BASE_META)(health_check_handler)

    def add_endpoint(
        self,
        name: str,
        path: str,
        handler: Callable,
        method: APIMethod = APIMethod.POST,
    ):
        """API method used to add a new endpoint to
        the current API. Endpoints required a name, path
        and handler function to be added.

        Args:
            name (str): name of endpoint
            path (str): REST path to use for endpoint
            handler (Callable): handler function
        """

        print(
            f"Adding {method.value} endpoint [bold green]{name}[/bold green] "
            f"with API endpoint [bold green]{path}[/bold green]"
        )

        if method == APIMethod.POST:
            # generate input and output data models for pydantic
            handler, response_model = generate_post_endpoint(handler, name)
            self.post(path, response_model=response_model, **ENDPOINT_META)(handler)

        elif method == APIMethod.GET:
            # generate output model only for GET endpoints
            handler, response_model = generate_get_endpoint(handler, name)
            self.get(path, response_model=response_model, **ENDPOINT_META)(handler)
