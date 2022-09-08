import importlib
import inspect
from typing import Callable

import typer
import yaml
import uvicorn
from rich import print
from pydantic import ValidationError

from tapi.cli.run.models import APIConfig
from tapi.api import TapiBaseAPI
from tapi.api.exceptions import (
    InvalidReturnTypeException,
    InvalidTypeException,
    MissingAnnotationException,
)


class InvalidHandlerFunctionException(Exception):
    """Exception raised when a non-function
    object is passed as a handler for a tapi
    endpoint"""


def get_endpoint_handler(handler: str) -> Callable:
    """Function used to retrieve python function
    from target module

    Args:
        handler (str): path to handler

    Returns:
        Callable: python function
    """

    *module_comps, func_name = handler.split(".")
    module_name = ".".join(module_comps)
    # import module and extract function
    module = importlib.import_module(module_name)

    func = getattr(module, func_name)
    if not inspect.isfunction(func):
        raise InvalidHandlerFunctionException
    return func


def get_api_config(config_path: str) -> APIConfig:
    """Function used to generate new API
    config class from YAML file

    Args:
        config_path (str): path of config file

    Returns:
        APIConfig: pydantic data model containing
        fields
    """

    with open(config_path, "r") as f:
        spec = yaml.safe_load(f)
    return APIConfig(**spec)


def run_command(config_path: str = "tapi.yml"):
    """CLI function used to generate new API
    from existing YAML configuration file

    Args:
        config_path (str, optional): Path to Tapi YAMl configuration
        file. Defaults to "tapi.yml".
    """

    try:

        spec = get_api_config(config_path)

    except FileNotFoundError:
        print(
            f"[bold red]ERROR:[/bold red] Unable to load config file. No such file '{config_path}'."
        )
        raise typer.Exit()

    except (yaml.YAMLError, ValidationError):
        print("[bold red]ERROR:[/bold red] Unable to parse YAML configuration file.")
        raise typer.Exit()

    print(
        "[bold green]SUCCESS:[/bold green] Loaded API config file. Generating service."
    )

    app = TapiBaseAPI()

    try:
        # iterate over provided endpoints and add handler
        for endpoint in spec.endpoints:
            # import API handler and add endpoint
            handler = get_endpoint_handler(endpoint.handler)
            app.add_endpoint(endpoint.name, endpoint.path, handler, endpoint.method)
    except (
        InvalidReturnTypeException,
        InvalidTypeException,
        MissingAnnotationException,
    ):
        print(
            "[bold red]ERROR:[/bold red]: Unable to generate API. Invalid function signature. "
            "Ensure that all arguments and return types are annotated with supported types"
        )
        raise typer.Exit()
    except InvalidHandlerFunctionException:
        print(
            "[bold red]ERROR:[/bold red]: Unable to generate API. Provided handler(s) must "
            "be valid python functions"
        )
        raise typer.Exit()
    except ModuleNotFoundError:
        print(
            "[bold red]ERROR:[/bold red]: Unable to generate API. Provided handlers cannot "
            "be imported"
        )
        raise typer.Exit()

    # run generated API with uvicorn server
    uvicorn.run(app, host=spec.listen_address, port=spec.listen_port)
