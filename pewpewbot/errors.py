from functools import wraps

from aiohttp import ClientError as AiohttpClientError
from marshmallow.exceptions import ValidationError as MarshmallowValidationError


class ClientError(Exception):
    pass


class AuthenticationError(ClientError):
    pass


class ConnectionError(ClientError):
    pass


class ValidationError(ClientError):
    pass


def wrap_errors(wrapped):
    @wraps(wrapped)
    async def wrapper(*args, **kwargs):
        try:
            return wrapped(*args, **kwargs)
        except AiohttpClientError as err:
            raise ConnectionError() from err
        except MarshmallowValidationError as err:
            raise ValidationError() from err
    return wrapper
