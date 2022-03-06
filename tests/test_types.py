import pytest
from moosetash.types import is_lambda, should_iterate


def dummy(value):
    return False


IS_LAMBDA_CASES = [
    ([], False),
    ({}, False),
    ('string', False),
    (lambda x: 'return', True),
    (dummy, True),
]


@pytest.mark.parametrize('test_input,expected', IS_LAMBDA_CASES)
def test_is_lambda(test_input, expected):
    assert is_lambda(test_input) == expected


SHOULD_ITERATE_CASES = [
    ([], True),
    ([1, 2, 3], True),
    (range(5), True),
    ('string', False),
]


@pytest.mark.parametrize('test_input,expected', SHOULD_ITERATE_CASES)
def test_should_iterate(test_input, expected):
    assert should_iterate(test_input) == expected
