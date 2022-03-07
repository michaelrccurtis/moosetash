"""Utilities for accessing rendering context"""
from typing import Any, List, Optional
from .exceptions import ContextAccessError, MissingVariable


def get(obj: Any, variable: str) -> Any:
    """Lookup key from obj"""
    try:
        return obj[variable]
    except (TypeError, AttributeError):
        pass
    except KeyError as ex:
        raise MissingVariable(variable) from ex

    try:
        return getattr(obj, variable)
    except (TypeError, AttributeError):
        pass

    try:
        return obj[int(variable)]
    except (IndexError, KeyError) as ex:
        raise MissingVariable(variable) from ex
    except ValueError:
        pass

    raise MissingVariable(variable)


def deep_get(context: Any, variable: str, units: Optional[List[str]] = None) -> Any:
    """Recursively fetch a variable from context"""
    if variable == '.':
        # Handle implicit interpolation
        return context

    value = context
    has_match = False

    if units is None:
        units = variable.split('.')

    for unit in units:
        try:
            value = get(value, unit)
        except MissingVariable as ex:
            if has_match:
                return None
            raise ex
        except Exception as ex:
            raise ContextAccessError(variable) from ex
        has_match = True
    return value


def get_from_context(contexts: List[Any], variable: str) -> Any:
    """Search list of context for a variable"""

    value = None
    units = variable.split('.')

    for context in reversed(contexts):
        try:
            value = deep_get(context, variable, units)
            break
        except MissingVariable:
            pass

    if value is None:
        raise MissingVariable(variable)

    return value
