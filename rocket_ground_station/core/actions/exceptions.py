class ActionError(Exception):
    """Base class for action exceptions"""


class DisarmedActionCallError(Exception):
    """Called attempted to call disarmed action"""

    def __init__(self, action_name, operation, *args: object) -> None:
        message = f'Cannot perform disarmed {action_name} {operation}'
        super().__init__(message, *args)
