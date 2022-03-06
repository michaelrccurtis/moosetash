"""Utilities for accessing rendering context"""
from typing import Any, List


class ContextAccessError(Exception):
    """Error getting a variable from context"""


def deep_get(context: Any, variable: str) -> Any:
    """Recursively fetch a variable from context"""

    if variable == '.':
        # Handle implicit interpolation
        return context

    units = variable.split('.')
    value = context
    has_match = False
    for unit in units:
        try:
            value = value[unit]
        except Exception as ex:
            if has_match:
                return None
            raise ContextAccessError('Error getting {variable}') from ex
        has_match = True
    return value


def get_from_context(contexts: List[Any], variable: str) -> Any:
    """Search list of context for a variable"""

    value = None

    for context in reversed(contexts):
        try:
            value = deep_get(context, variable)
            break
        except ContextAccessError:
            pass

    if value is None:
        # Raise here
        value = ''
    return value
