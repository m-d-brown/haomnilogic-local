"""Exceptions for the shadow library."""


class OmniLogicException(Exception):
    """Base class for all OmniLogic exceptions."""


class OmniEquipmentNotInitializedError(OmniLogicException):
    """Error to indicate that equipment has not been initialized."""
