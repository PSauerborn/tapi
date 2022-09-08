from uuid import UUID
from datetime import datetime, date
from typing import List, Dict, Literal

from fastapi.responses import JSONResponse

# define allowed types when defining algorithms
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

ENDPOINT_META = {
    "tags": ["Function Endpoints"],
    "response_class": JSONResponse,
}
