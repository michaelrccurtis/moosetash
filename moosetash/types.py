from typing import Any, Callable
from .exceptions import LambdaException


def is_lambda(context: Any) -> bool:
    """Shoule we traeat context value as a lambda?"""
    return callable(context)


def invoke_lambda(
    func: Callable,
    *,
    name: str,
    template: str = None,
) -> str:
    try:
        invoked = func() if template is None else func(template)

        if not isinstance(invoked, (str, int, float)):
            raise LambdaException(f'Unexpected return type from lambda "{name}"')

        return str(invoked)
    except Exception as ex:
        raise LambdaException(str(ex)) from ex


def should_iterate(context: Any) -> bool:
    """Should we iterate context value?"""

    if isinstance(context, str) or isinstance(context, dict):
        return False
    try:
        _ = iter(context)
        return True
    except TypeError:
        return False
