import inspect
from typing import Callable, Any

from pydantic import BaseModel, create_model

from tapi.api.constants import ALLOWED_TYPES
from tapi.api.exceptions import (
    InvalidTypeException,
    MissingAnnotationException,
    InvalidReturnTypeException,
)


def replace_function_signature(func: Callable, target: Callable) -> Callable:
    """Function used to replace function
    signature of a target function with
    the signature of another function. This
    ensures that wrapped execution functions
    have the same signature as the functions
    they are wrapping

    Args:
        func (Callable): function with desired signature
        target (Callable): function to modify

    Returns:
        Callable: function with modified signature
    """

    signature = inspect.signature(func)
    target.__signature__ = signature
    return target


def is_allowed_type(_type: Any) -> bool:
    """Function used to determine if provided
    type is allowed

    Args:
        _type (Any): type to check

    Returns:
        bool: true if type is allowed else
        false
    """

    # allow all instanced of pydantic models
    # to ensure full integration with pydantic
    if inspect.isclass(_type) and issubclass(_type, BaseModel):
        return True
    elif _type in ALLOWED_TYPES:
        return True

    # get underlying properties of type. non-container
    # types (sets for instance) do not have this property
    # and are not allowed
    properties = getattr(_type, "__dict__", None)
    if properties is None:
        return False

    # get arguments for container types (dicts, lists etc).
    # if this is None, assume that type is basic and not
    # in allowed types
    arguments = properties.get("__args__")
    if arguments is None:
        return False

    for arg in arguments:
        if not is_allowed_type(arg):
            return False
    return True


def validate_callable(func: Callable):
    """Function used to validate a given
    callable to ensure that provided function
    is annotated correctly and all types are
    valid

    Args:
        func (Callable): tapi function to validate
    """

    # get all annotations that are not return types
    annotations = func.__annotations__
    var_annotations = {k: v for k, v in annotations.items() if k != "return"}

    # get function signature and check for missing
    # annotations
    f_args = inspect.signature(func)
    missing = [a for a in f_args.parameters.keys() if a not in var_annotations]
    if missing:
        raise MissingAnnotationException(
            "Unable to generate data model: " f"missing annotations for '{missing}'"
        )

    for k, v in annotations.items():
        # raise exception if provided type
        # is not in whitelist of types
        if not is_allowed_type(v):
            raise InvalidTypeException(
                "Unable to generate data model: " f"argument {k} has invalid type {v}"
            )

    return_type = annotations.get("return")
    if not is_allowed_type(return_type):
        raise InvalidReturnTypeException(
            "Unable to generate data model: " f"return type {return_type} is invalid"
        )


def generate_input_model(func: Callable, name: str) -> BaseModel:
    """Function used to generate input pydantic
    model for a given function

    Args:
        func (Callable): function to generate input
            model for
        name (str): name of endpoint. Used to name model

    Returns:
        BaseModel: Pydantic data model containing fields
            for input
    """

    validate_callable(func)

    # get all annotations that are not return types
    annotations = func.__annotations__
    annotations = {k: v for k, v in annotations.items() if k != "return"}

    fields = {k: (_type, ...) for k, _type in annotations.items()}
    # generate a model hash (names for generated models need to be unique)
    model_hash = f"InputModel - {name}"
    return create_model(model_hash, **fields)


def generate_output_model(func: Callable, name: str) -> BaseModel:
    """Function used to generate output pydantic
    model for a given function

    Args:
        func (Callable): function to generate output
            model for
        name (str): name of endpoint. Used to name model

    Returns:
        BaseModel: Pydantic data model containing fields
            for output
    """

    validate_callable(func)

    annotations = func.__annotations__
    return_type = annotations.get("return")

    # if return type is a pydantic model, return unmodified
    if inspect.isclass(return_type) and issubclass(return_type, BaseModel):
        return return_type
    # generate a model hash (names for generated models need to be unique)
    model_hash = f"OutputModel - {name}"
    return create_model(model_hash, **{"result": (return_type, ...)})
