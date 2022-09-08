import json
import unittest
from asyncio import get_event_loop

from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from tapi.api.base_api import (
    TapiBaseAPI,
    generate_get_endpoint,
    generate_post_endpoint,
    APIMethod,
)
from tests.api.sample_functions import (
    execute_addition,
    execute_subtraction,
    execute_divide,
)


class BaseAPIUnittests(unittest.TestCase):
    def test_generate_get_endpoint(self):
        """Test endpoint used to generate GET endpoint
        from python function handler"""

        # generate data model and handler function
        # for execute_addition
        handler, model = generate_get_endpoint(execute_addition, "test-function")

        try:
            # ensure that response model matches expected signature
            model(**{"result": 10})
        except ValidationError:
            self.fail()

        self.assertRaises(ValidationError, model, **{"result": "not an int"})
        # generate new event loop and run async handler
        # and run handler function using loop
        loop = get_event_loop()
        result = loop.run_until_complete(handler(5, 10))

        self.assertIsInstance(result, JSONResponse)
        # parse raw JSON content and validate response
        json_content = result.body.decode()
        self.assertEqual(json.loads(json_content), {"result": 15, "http_code": 200})

    def test_generate_post_endpoint(self):
        """Test function used to generate new POST
        endpoint from python handler"""

        # generate data model and handler function
        # for execute_addition
        handler, model = generate_post_endpoint(execute_addition, "test-function")

        try:
            # ensure that response model matches expected signature
            model(**{"result": 10})
        except ValidationError:
            self.fail()

        self.assertRaises(ValidationError, model, **{"result": "not an int"})

        # generate new instance of request body
        class InputModel(BaseModel):
            x: int
            y: int

        request_body = InputModel(x=10, y=5)
        # generate new event loop and run async handler
        # and run handler function using loop
        loop = get_event_loop()
        result = loop.run_until_complete(handler(request_body))

        self.assertIsInstance(result, JSONResponse)
        # parse raw JSON content and validate response
        json_content = result.body.decode()
        self.assertEqual(json.loads(json_content), {"result": 15, "http_code": 200})

    def test_base_api(self):
        """Test TapiBaseAPI module containing core functions"""

        app = TapiBaseAPI()
        # add two endpoints, one for subtraction one for addition
        app.add_endpoint("test-addition", "/add", execute_addition)
        app.add_endpoint("test-division", "/divide", execute_divide)
        app.add_endpoint(
            "test-subtraction",
            "/subtract",
            execute_subtraction,
            APIMethod.GET,
        )

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/health_check")
        self.assertEqual(
            response.json(), {"http_code": 200, "message": "Service is running"}
        )

        response = client.post("/add", json={"x": 5, "y": 10})
        self.assertEqual(response.json(), {"http_code": 200, "result": 15})

        response = client.get("/subtract?x=5&y=1")
        self.assertEqual(response.json(), {"http_code": 200, "result": 4})

        # test error handling and parsing
        response = client.get("/not-found")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"http_code": 404, "message": "Not Found"})

        response = client.post("/divide", json={"x": 5, "y": 0})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(), {"http_code": 500, "message": "Internal server error"}
        )
