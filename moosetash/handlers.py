from typing import Any
from .exceptions import MissingPartial, MissingVariable


def missing_variable_default(variable_name: str, variable_tag: str) -> str:
    return ''


def missing_variable_raise(variable_name: str, variable_tag: str):
    raise MissingVariable(variable_name)


def missing_variable_keep(variable_name: str, variable_tag: str) -> str:
    return variable_tag


def missing_partial_default(partial_name: str, partial_tag: str) -> str:
    return ''


def missing_partial_raise(partial_name: str, partial_tag: str) -> str:
    raise MissingPartial(partial_name)


def missing_partial_keep(partial_name: str, partial_tag: str) -> str:
    return partial_tag


def default_serializer(value: Any) -> str:
    """By default, serialize variables as by stringifying"""
    return str(value)
