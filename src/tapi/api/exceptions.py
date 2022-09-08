class InvalidTypeException(Exception):
    """Exception raised when an invalid type
    is provided"""


class MissingAnnotationException(Exception):
    """Exception raised if an annotation is missing
    from a given API function"""


class InvalidReturnTypeException(Exception):
    """Exception raised when an invalid return
    type is provided for an API function"""
