from typing import List, Literal

from pydantic import BaseModel

from tapi.api.base_api import APIMethod


class APIEndpoint(BaseModel):

    name: str
    path: str
    method: APIMethod
    handler: str


class APIConfig(BaseModel):

    name: str
    listen_address: str = "0.0.0.0"
    listen_port: int = 8080
    endpoints: List[APIEndpoint]
