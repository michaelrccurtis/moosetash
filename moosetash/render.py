"""Render a Mustache template"""
from typing import Any
from typing import Callable as CallableType
from typing import Dict, List, Optional
from html import escape
from .context import MissingVariable, get_from_context
from .exceptions import MustacheSyntaxError
from .handlers import default_serializer, missing_partial_default, missing_variable_default
from .tokenizer import Token, tokenize
from .types import should_iterate


# pylint:disable=too-many-locals,too-many-branches,too-many-statements,too-many-arguments
def render(
    template: str,
    context: Dict,
    serializer: Optional[CallableType[[Any], str]] = None,
    partials: Optional[Dict] = None,
    missing_variable_handler: Optional[CallableType[[str, str], str]] = None,
    missing_partial_handler: Optional[CallableType[[str, str], str]] = None,
) -> str:
    """Render a mustache template"""

    serializer = serializer or default_serializer
    missing_variable_handler = missing_variable_handler or missing_variable_default
    missing_partial_handler = missing_partial_handler or missing_partial_default

    partials = partials or {}

    output: str = ''
    context_stack: List = [context]
    env_stack: List = []
    left_delimiter: str = '{{'
    right_delimiter: str = '}}'
    pointer: int = 0

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
                    pointer,
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
            output += serializer(variable)

        elif token is Token.VARIABLE:
            output += escape(serializer(variable))

        elif token in [Token.SECTION, Token.INVERTED]:
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

    return output
