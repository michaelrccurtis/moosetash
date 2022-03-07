from typing import Any


def is_lambda(context: Any) -> bool:
    """Shoule we traeat context value as a lambda?"""
    return callable(context)


def should_iterate(context: Any) -> bool:
    """Should we iterate context value?"""

    if isinstance(context, str) or isinstance(context, dict):
        return False
    try:
        _ = iter(context)
        return True
    except TypeError:
        return False
