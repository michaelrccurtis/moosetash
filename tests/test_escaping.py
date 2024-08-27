import pytest

from moosetash import render

ESCAPING_CASES = [
    ('{{variable}}', {'variable': 'A & B'}, True, 'A &amp; B'),
    ('{{variable}}', {'variable': 'A & B'}, False, 'A & B'),
]


@pytest.mark.parametrize('template,context,escape_html,expected', ESCAPING_CASES)
def test_custom_serializer(template, context, escape_html, expected):
    assert render(template, context, escape_html=escape_html) == expected
