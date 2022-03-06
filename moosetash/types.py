from typing import Any
from collections.abc import Iterator, Sequence


def is_lambda(context: Any) -> bool:
    """Shoule we traeat context value as a lambda?"""
    return callable(context)


def should_iterate(context: Any) -> bool:
    """Should we iterate context value?"""
    return isinstance(context, (Sequence, Iterator)) and not isinstance(context, str)
