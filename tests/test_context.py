from unittest.mock import Mock
import pytest
from moosetash.context import ContextAccessError, MissingVariable, deep_get, get, get_from_context


class Dummy:
    @property
    def prop(self):
        return 'property'

    def __getattr__(self, key):
        return key


GET_CASES = [
    ({'variable': 'variable'}, 'variable', 'variable'),
    (Mock(a='variable'), 'a', 'variable'),
    ([0, 1, 2], '1', 1),
    (range(3), '1', 1),
    (Dummy(), 'prop', 'property'),
    (Dummy(), 'key', 'key'),
]


@pytest.mark.parametrize('context,variable,expected', GET_CASES)
def test_get(context, variable, expected):
    assert get(context, variable) == expected


GET_MISSING_CASES = [([1, 2, 3], '4'), ({}, 'key')]


@pytest.mark.parametrize('context,variable', GET_MISSING_CASES)
def test_get_missing(context, variable):
    with pytest.raises(MissingVariable, match=variable):
        get(context, variable)


DEEP_GET_CASES = [
    ({'variable': 'variable'}, 'variable', 'variable'),
    ({'variable': 1}, 'variable', 1),
    ({'variable': [1, 2, 3]}, 'variable', [1, 2, 3]),
    ({'nested': {'variable': 'variable'}}, 'nested.variable', 'variable'),
    ({'a': {'b': {'c': {'d': {'e': 'variable'}}}}}, 'a.b.c.d.e', 'variable'),
    ({'a': {'b': {'c': {'d': {'e': {}}}}}}, 'a.b.c.d.e.f', None),
    ({'a': Mock(b='variable')}, 'a.b', 'variable'),
]


@pytest.mark.parametrize('context,variable,expected', DEEP_GET_CASES)
def test_deep_get(context, variable, expected):
    assert deep_get(context, variable) == expected


class DummyRaiser:
    @property
    def test(self):
        raise EnvironmentError('error')


def test_deep_get_error():
    with pytest.raises(ContextAccessError, match='test'):
        deep_get(DummyRaiser(), 'test')


GET_FROM_CONTEXT_CASES = [
    ([{'a': 'b', 'c': 1}, {'c': 2}], 'c', 2),
    ([{'a': 'b', 'c': 1}, {'c': 2}], 'a', 'b'),
]


@pytest.mark.parametrize('contexts,variable,expected', GET_FROM_CONTEXT_CASES)
def test_get_from_context(contexts, variable, expected):
    assert get_from_context(contexts, variable) == expected
