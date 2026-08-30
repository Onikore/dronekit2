"""Exception types used throughout dronekit."""


class APIException(Exception):
    """
    Base class for DroneKit related exceptions.

    :param String message: Message string describing the exception
    """


class TimeoutError(APIException):
    """Raised by operations that have timeouts."""
