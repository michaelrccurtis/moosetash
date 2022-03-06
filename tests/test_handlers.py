import datetime as dt
import pytest
from moosetash import (
    MissingPartial,
    MissingVariable,
    default_serializer,
    missing_partial_default,
    missing_partial_keep,
    missing_partial_raise,
    missing_variable_default,
    missing_variable_keep,
    missing_variable_raise,
)


def test_missing_variable_default():
    assert missing_variable_default('name', '{{ name }}') == ''


def test_missing_variable_raise():
    with pytest.raises(MissingVariable, match='name'):
        assert missing_variable_raise('name', '{{ name }}') == ''


def test_missing_variable_keep():
    assert missing_variable_keep('name', '{{ name }}') == '{{ name }}'


def test_missing_partial_default():
    assert missing_partial_default('name', '{{>name}}') == ''


def test_missing_partial_raise():
    with pytest.raises(MissingPartial, match='name'):
        assert missing_partial_raise('name', '{{>name}}') == ''


def test_missing_partial_keep():
    assert missing_partial_keep('name', '{{>name}}') == '{{>name}}'


class Dummy:
    def __str__(self):
        return 'DUMMY STRING'


SERIALIZER_CASES = [
    (1, '1'),
    ('string', 'string'),
    (dt.date(2020, 9, 1), '2020-09-01'),
    (Dummy(), 'DUMMY STRING'),
]


@pytest.mark.parametrize('test_input,expected', SERIALIZER_CASES)
def test_default_serializer(test_input, expected):
    assert default_serializer(test_input) == expected
