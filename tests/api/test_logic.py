import unittest
import inspect
from typing import Dict, List, Set

from pydantic import ValidationError

from tapi.api.logic import (
    is_allowed_type,
    replace_function_signature,
    validate_callable,
    generate_input_model,
    generate_output_model,
)
from tapi.api.exceptions import (
    InvalidReturnTypeException,
    InvalidTypeException,
    MissingAnnotationException,
)


class LogicUnittests(unittest.TestCase):
    def test_is_allowed_type(self):
        """Test function used to determine if a specific
        type is allowed when defining algorithms"""

        # assert that allowed types are handled correctly
        allowed_types = [
            int,
            float,
            str,
            bool,
            Dict,
            List,
            Dict[str, float],
            Dict[str, Dict[str, float]],
            List[int],
            List[Dict[str, float]],
            List[Dict[str, List[Dict[str, float]]]],
        ]
        for t in allowed_types:
            self.assertTrue(is_allowed_type(t))

        # assert that invalid types are handled correctly
        disallowed_types = [
            tuple,
            Dict[str, tuple],
            set(),
            List[tuple],
            List[Dict[str, Dict[str, tuple]]],
        ]
        for t in disallowed_types:
            self.assertFalse(is_allowed_type(t))

    def test_replace_function_signature(self):
        """Test function used to replace one functions
        signature with another"""

        def test_function(x: int, y: int):
            return x + y

        def target_function(y: str):
            return

        # replace signature on target function with
        # test function signature
        target_function = replace_function_signature(test_function, target_function)
        signature = inspect.signature(target_function)
        # check that signature has been overridden
        self.assertEqual(signature.parameters["x"].annotation, int)
        self.assertEqual(signature.parameters["y"].annotation, int)

    def test_validate_callable(self):
        """Test function used to validate callable
        instances for API generation"""

        def test_valid(x: int, y: int) -> int:
            return x + y

        self.assertIsNone(validate_callable(test_valid))

        def test_missing(x: int, y) -> int:
            return x + y

        self.assertRaises(MissingAnnotationException, validate_callable, test_missing)

        def test_missing_return(x: int, y: int):
            return x + y

        self.assertRaises(
            InvalidReturnTypeException, validate_callable, test_missing_return
        )

        def test_invalid_type(x: int, y: Set) -> int:
            return x + y

        self.assertRaises(InvalidTypeException, validate_callable, test_invalid_type)

        def test_invalid_return_type(x: int, y: int) -> Set:
            return x + y

        self.assertRaises(
            InvalidTypeException, validate_callable, test_invalid_return_type
        )

    def test_generate_input_model(self):
        """Test function used to generate input
        models from a given function signature"""

        def test_function(x: int, y: float) -> float:
            return x * y

        model = generate_input_model(test_function, "test-function")

        try:
            model(**{"x": 10, "y": 15.2})
        except ValidationError:
            self.fail()

        self.assertRaises(ValidationError, model, **{"x": 10, "y": "not a float"})

    def test_generate_output_model(self):
        """Test function used to generate output
        models from a given function signature"""

        def test_function(x: int, y: float) -> float:
            return x * y

        model = generate_output_model(test_function, "test-function")

        try:
            model(result=10.5)
        except ValidationError:
            self.fail()

        self.assertRaises(ValidationError, model, **{"result": "not a float"})
