"""Render a Mustache template"""
from html import escape
from typing import Any, Dict, List, Optional
from typing import Callable as CallableType

from .context import MissingVariable, get_from_context
from .exceptions import MustacheSyntaxError
from .handlers import (
    default_serializer,
    missing_partial_default,
    missing_variable_default,
)
from .tokenizer import Token, tokenize
from .types import invoke_lambda, is_lambda, should_iterate


def find_closing_pointer_limits_cached(current_pointer: int, section_name: str, tokens):
    count = 1
    previous_position_pointer = tokens[current_pointer][1]
    for idx, ((token, value, _), position_pointer) in enumerate(tokens[current_pointer:]):
        if section_name == value:
            if token in [Token.SECTION, Token.INVERTED]:
                count += 1

            if token is Token.END:
                count -= 1

            if count == 0:
                return previous_position_pointer, current_pointer + idx + 1
        previous_position_pointer = position_pointer
    return None, None


def find_closing_pointer_limits(
    current_pointer: int,
    section_name: str,
    iterator,
):
    count = 1
    previous_pointer = current_pointer
    for (token, value, _), pointer in iterator:
        if section_name == value:
            if token in [Token.SECTION, Token.INVERTED]:
                count += 1

            if token is Token.END:
                count -= 1

            if count == 0:
                return previous_pointer, pointer
        previous_pointer = pointer
    return None, None


# pylint:disable=too-many-locals,too-many-branches,too-many-statements,too-many-arguments
def render(
    template: str,
    context: Dict,
    serializer: Optional[CallableType[[Any], str]] = None,
    partials: Optional[Dict] = None,
    missing_variable_handler: Optional[CallableType[[str, str], str]] = None,
    missing_partial_handler: Optional[CallableType[[str, str], str]] = None,
    left_delimiter: Optional[str] = None,
    right_delimiter: Optional[str] = None,
    cache_tokens: bool = False,
    escape_html: bool = True,
) -> str:
    """Render a mustache template"""

    serializer = serializer or default_serializer
    missing_variable_handler = missing_variable_handler or missing_variable_default
    missing_partial_handler = missing_partial_handler or missing_partial_default

    partials = partials or {}

    output: str = ''
    context_stack: List = [context]
    env_stack: List = []
    pointer: int = 0

    left_delimiter = left_delimiter or '{{'
    right_delimiter = right_delimiter or '}}'

    tokens = []

    if cache_tokens:
        tokens = list(tokenize(template, 0, left_delimiter, right_delimiter))

    while True:
        if cache_tokens:
            try:
                (token, value, indentation), position_pointer = tokens[pointer]
                pointer += 1
            except IndexError:
                break
        else:
            try:
                (token, value, indentation), pointer = next(
                    tokenize(template, pointer, left_delimiter, right_delimiter)
                )
                position_pointer = pointer
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

            env_name, env_pointer, [env_var, _] = current_env

            if should_iterate(env_var):
                current_env[2][1] += 1
                try:
                    next_item = env_var[current_env[2][1]]
                    context_stack.append(next_item)
                    pointer = env_pointer
                    continue
                except IndexError:
                    pass

            if env_name != value:
                raise MustacheSyntaxError.from_template_pointer(
                    f'Unexpected section end tag on line {{line_number}}. Expected "{env_name}" got "{value}"',
                    template,
                    position_pointer,
                )

            env_stack.pop()

        if not current_context and len(context_stack) != 1:
            if token in [Token.SECTION, Token.INVERTED]:
                context_stack.append(False)
                env_stack.append([value, pointer, [False, 0]])
            continue

        if token in [Token.NO_ESCAPE, Token.VARIABLE, Token.SECTION, Token.INVERTED]:
            try:
                variable = get_from_context(context_stack, value)
            except MissingVariable:
                variable = missing_variable_handler(
                    value, f'{left_delimiter} {value} {right_delimiter}'
                )
        else:
            variable = None

        if token is Token.LITERAL:
            output += value

        elif token is Token.NO_ESCAPE:
            if is_lambda(variable):
                variable = render(
                    invoke_lambda(variable, name=value),
                    current_context,
                    serializer=serializer,
                    partials=partials,
                )
            output += serializer(variable)

        elif token is Token.VARIABLE:
            if is_lambda(variable):
                variable = render(
                    invoke_lambda(variable, name=value),
                    current_context,
                    serializer=serializer,
                    partials=partials,
                )

            if escape_html:
                output += escape(serializer(variable))
            else:
                output += serializer(variable)

        elif token in [Token.SECTION, Token.INVERTED]:
            if token is Token.INVERTED:
                if is_lambda(variable):
                    variable = False
                else:
                    variable = not variable

            if not variable:
                if cache_tokens:
                    _, skip_pointer = find_closing_pointer_limits_cached(pointer, value, tokens)
                else:
                    _, skip_pointer = find_closing_pointer_limits(
                        position_pointer,
                        value,
                        tokenize(template, pointer, left_delimiter, right_delimiter),
                    )
                if skip_pointer is not None:
                    pointer = skip_pointer
                    continue

                raise MustacheSyntaxError.from_template_pointer(
                    f'Unclosed section "{value}" beginning on line {{line_number}}',
                    template,
                    position_pointer,
                )

            if is_lambda(variable):
                if cache_tokens:
                    section_end_pointer, skip_pointer = find_closing_pointer_limits_cached(
                        pointer, value, tokens
                    )
                else:
                    section_end_pointer, skip_pointer = find_closing_pointer_limits(
                        position_pointer,
                        value,
                        tokenize(template, pointer, left_delimiter, right_delimiter),
                    )

                if skip_pointer is not None:
                    lambda_output = render(
                        invoke_lambda(
                            variable,
                            name=value,
                            template=template[position_pointer:section_end_pointer],
                        ),
                        current_context,
                        serializer=serializer,
                        partials=partials,
                        left_delimiter=left_delimiter,
                        right_delimiter=right_delimiter,
                    )
                    output += lambda_output
                    pointer = skip_pointer
                    continue

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
            partial_template = partials.get(value)  # potentially raise error here
            if partial_template is None:
                partial_template = missing_partial_handler(
                    value, f'{left_delimiter} {value} {right_delimiter}'
                )

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

        elif token is Token.PARENT:
            partial_template = partials.get(value)  # potentially raise error here
            if partial_template is None:
                partial_template = missing_partial_handler(
                    value, f'{left_delimiter} {value} {right_delimiter}'
                )
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

            if cache_tokens:
                section_end_pointer, skip_pointer = find_closing_pointer_limits_cached(
                    pointer, value, tokens
                )
            else:
                section_end_pointer, skip_pointer = find_closing_pointer_limits(
                    position_pointer,
                    value,
                    tokenize(template, pointer, left_delimiter, right_delimiter),
                )

            pointer = skip_pointer

        elif token is Token.SUBSTITUTION:
            context_stack.append(True)
            env_stack.append([value, pointer, [None, 0]])

    return output
