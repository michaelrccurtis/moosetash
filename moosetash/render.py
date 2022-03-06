"""Render a Mustache template"""
from typing import Any
from typing import Callable as CallableType
from typing import Dict, List, Optional
from collections.abc import Iterator, Sequence
from html import escape
from .context import get_from_context
from .tokenizer import Token, tokenize


def is_lambda(context: Any) -> bool:
    """Shoule we traeat context value as a lambda?"""
    return callable(context)


def should_iterate(context: Any) -> bool:
    """Should we iterate context value?"""
    return isinstance(context, (Sequence, Iterator)) and not isinstance(context, str)


def default_serializer(value: Any) -> str:
    """By default, serialize variables as by stringifying"""
    return str(value)


# pylint:disable=too-many-locals,too-many-branches,too-many-statements
def render(
    template: str,
    context: Dict,
    serializer: Optional[CallableType[[Any], str]] = None,
    partials: Optional[Dict] = None,
) -> str:
    """Render a mustache template"""

    serializer = serializer or default_serializer
    partials = partials or {}

    output = ''
    context_stack: List = [context]
    env_stack: List = []
    left_delimiter: str = '{{'
    right_delimiter: str = '}}'
    pointer = 0
    while True:
        try:
            (token, value, indentation), pointer = next(
                tokenize(template, pointer, left_delimiter, right_delimiter)
            )
        except StopIteration:
            break

        current_context = context_stack[-1]

        if token is Token.SET_DELIMITER:
            new_delimiters = value.strip().split(' ')
            left_delimiter = new_delimiters[0]
            right_delimiter = new_delimiters[-1]

        if token is Token.END:
            current_env = env_stack[-1]
            context_stack.pop()

            _, env_pointer, [env_var, _] = current_env

            if should_iterate(env_var):
                current_env[2][1] += 1
                try:
                    next_item = env_var[current_env[2][1]]
                    context_stack.append(next_item)
                    pointer = env_pointer
                    continue
                except IndexError:
                    pass
            # Check env is as expected
            env_stack.pop()

        if not current_context and len(context_stack) != 1:
            if token in [Token.SECTION, Token.INVERTED]:
                context_stack.append(False)
                env_stack.append([value, pointer, [False, 0]])
            continue

        if token is Token.LITERAL:
            output += value

        elif token is Token.NO_ESCAPE:
            output += serializer(get_from_context(context_stack, value))

        elif token is Token.VARIABLE:
            output += escape(serializer(get_from_context(context_stack, value)))

        elif token in [Token.SECTION, Token.INVERTED]:
            variable = get_from_context(context_stack, value)

            if token is Token.INVERTED:
                variable = not variable

            if should_iterate(variable):
                try:
                    context_item = variable[0]
                    context_stack.append(context_item)
                except IndexError:
                    context_stack.append(False)
            else:
                context_stack.append(variable)
            env_stack.append([value, pointer, [variable, 0]])

        elif token is Token.PARTIAL:

            partial_template = partials.get(value, '')  # potentially raise error here

            if partial_template != '':
                remove_trailing_indentation = False
                if partial_template.endswith('\n'):
                    remove_trailing_indentation = True

                partial_template = indentation + f'\n{indentation}'.join(
                    partial_template.split('\n')
                )

                if remove_trailing_indentation:
                    partial_template = partial_template[: -len(indentation)]

                partial_output = render(
                    partial_template, current_context, serializer=serializer, partials=partials
                )
                output += partial_output

    return output
