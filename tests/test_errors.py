from typing import Any, List, Tuple
import pytest
from moosetash import LambdaException, MustacheSyntaxError, render

SYNTAX_ERRORS: List[Tuple[str, Any, str]] = [
    ('{{ variable', {}, 'Unclosed tag on line 1'),
    ('\n{{ different }}\n{{ variable', {}, 'Unclosed tag on line 3'),
    ('{{{ variable}}', {}, 'Unclosed tag on line 1'),
    ('\n{{= variable}}', {}, 'Unclosed tag on line 2'),
    (
        '{{#variable}}{{/bad}}',
        {'variable': 'variable'},
        'Unexpected section end tag on line 1. Expected "variable" got "bad',
    ),
    (
        '{{^variable}}{{test}}',
        {'variable': True},
        'Unclosed section "variable" beginning on line 1',
    ),
]


@pytest.mark.parametrize('test_input,context,expected', SYNTAX_ERRORS)
def test_syntax_error(test_input, context, expected):
    with pytest.raises(MustacheSyntaxError, match=expected):
        render(test_input, context)


LAMBDA_ERRORS: List[Tuple[str, Any, str]] = [
    ('{{ func }}', {'func': lambda: {}}, 'Unexpected return type from lambda "func"'),
]


@pytest.mark.parametrize('test_input,context,expected', LAMBDA_ERRORS)
def test_lambda_error(test_input, context, expected):
    with pytest.raises(LambdaException, match=expected):
        render(test_input, context)
