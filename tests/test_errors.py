from typing import Any, List, Tuple
import pytest
from moosetash import MustacheSyntaxError, render

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
]


@pytest.mark.parametrize('test_input,context,expected', SYNTAX_ERRORS)
def test_find_next_tag(test_input, context, expected):
    with pytest.raises(MustacheSyntaxError, match=expected):
        render(test_input, context)
