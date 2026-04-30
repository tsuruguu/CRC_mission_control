class GroundStationError(Exception):
    """Base class for all exceptions used in project"""


class InvalidConfigError(GroundStationError):
    """Raised when one of the config entries is invalid"""


class TabNotImplementedError(GroundStationError):
    """Raised when Tab of requested type is not implemented"""


class DeviceNotImplementedError(GroundStationError):
    """Raised when Device of requested type is not implemented"""

class DeviceWidgetNotImplementedError(GroundStationError):
    """Raised when Device Widget of requested type is not implemented"""

class BadSequenceDescriptionError(GroundStationError):
    """Raised when there isn't enough information in to describe a sequence."""

    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.message = message


class BadConfigFormatError(GroundStationError):
    """Raised when configuration file contains objects that couldn't be handled by converter"""
