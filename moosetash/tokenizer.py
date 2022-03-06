"""Generate tokens from a mustache template"""
from typing import Iterator, Tuple
from enum import Enum
from .exceptions import MustacheSyntaxError


class Token(Enum):
    """Mustache token type"""

    LITERAL = 'LITERAL'
    VARIABLE = 'VARIABLE'
    COMMENT = '!'
    SECTION = '#'
    INVERTED = '^'
    END = '/'
    PARTIAL = '>'
    SET_DELIMITER = '='
    NO_ESCAPE_BRACE = '{'
    NO_ESCAPE = '&'


def find_next_tag(template: str, pointer: int, left_delimiter: str) -> Tuple[str, int]:
    """Find the next tag, and the literal between current pointer and that tag"""

    split_index = template.find(left_delimiter, pointer)

    if split_index == -1:
        return (template[pointer:], len(template))

    return (template[pointer:split_index], split_index)


def parse_tag(
    template: str, pointer: int, left_delimiter: str, right_delimiter: str
) -> Tuple[Tuple[Token, str], int]:
    """Parse a tag from a template"""
    tag_pointer = pointer + len(left_delimiter)

    try:
        token = Token(template[tag_pointer])
        tag_pointer += 1
    except ValueError:
        token = Token.VARIABLE

    if token is Token.NO_ESCAPE_BRACE:
        right_delimiter = f'}}{right_delimiter}'
        token = Token.NO_ESCAPE
    elif token is Token.SET_DELIMITER:
        right_delimiter = f'={right_delimiter}'

    tag_end_pointer = template.find(right_delimiter, tag_pointer)

    if tag_end_pointer == -1:
        raise MustacheSyntaxError.from_template_pointer(
            'Unclosed tag on line {line_number}', template, pointer
        )

    tag = template[tag_pointer:tag_end_pointer]

    return ((token, tag.strip()), tag_end_pointer + len(right_delimiter))


def find_next_pointer(
    template: str, tag_start_pointer: int, tag_end_pointer: int
) -> Tuple[bool, int, int]:
    """Find the next parsing pointer, based on the current tag and whether it is a standalone"""
    pre_tag_line = template.rfind('\n', 0, tag_start_pointer)
    post_tag_line = template.find('\n', tag_end_pointer)

    indentation_pointer = pre_tag_line
    if pre_tag_line == -1:
        pre_tag_line = 0
        indentation_pointer = 0
    else:
        indentation_pointer += 1

    before_tag = template[pre_tag_line:tag_start_pointer]
    after_tag = template[tag_end_pointer:post_tag_line]
    is_standalone = (before_tag.isspace() or before_tag == '') and (
        after_tag.isspace() or after_tag == ''
    )

    if post_tag_line == -1:
        post_tag_line = len(template)
    else:
        # Skip the newline character
        post_tag_line += 1
    return (
        is_standalone,
        post_tag_line if is_standalone else tag_end_pointer,
        indentation_pointer if is_standalone else tag_start_pointer,
    )


def tokenize(
    template: str, pointer: int = 0, left_delimiter: str = '{{', right_delimiter: str = '}}'
) -> Iterator[Tuple[Tuple[Token, str, str], int]]:
    """Generate tokens from a template string"""

    while pointer < len(template):
        literal, tag_start_pointer = find_next_tag(template, pointer, left_delimiter)
        indentation = ''

        if tag_start_pointer == len(template):
            # Reached the end of the template - return the final literal and end iteration
            yield (Token.LITERAL, literal, ''), len(template)
            break

        (token, token_value), tag_end_pointer = parse_tag(
            template, tag_start_pointer, left_delimiter, right_delimiter
        )

        if token is Token.SET_DELIMITER:
            new_delimiters = token_value.strip().split(' ')
            left_delimiter = new_delimiters[0]
            right_delimiter = new_delimiters[-1]

        if token not in [Token.VARIABLE, Token.NO_ESCAPE]:
            is_standalone, pointer, indentation_pointer = find_next_pointer(
                template, tag_start_pointer, tag_end_pointer
            )

            if is_standalone:
                if tag_start_pointer - indentation_pointer > 0:
                    literal = literal[0 : -(tag_start_pointer - indentation_pointer)]

                if token is Token.PARTIAL:
                    indentation = template[indentation_pointer:tag_start_pointer]

        else:
            # Variable interpolation tags cannot be standalones
            pointer = tag_end_pointer

        if literal != '':
            yield (Token.LITERAL, literal, ''), tag_start_pointer

        # Comments and set delimiters do not appear in output
        if token not in [Token.COMMENT]:
            yield (token, token_value, indentation), pointer
