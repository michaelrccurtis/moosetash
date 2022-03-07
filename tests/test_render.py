from typing import Any
import datetime as dt
import pytest
from moosetash import render


def date_serializer(value: Any) -> str:

    if isinstance(value, dt.date):
        return value.strftime('%d-%m/%Y')

    return str(value)


CUSTOM_SERIALIZER_CASES = [
    ('{{variable}}', {'variable': dt.date(2020, 1, 10)}, date_serializer, '10-01/2020'),
    ('{{variable}}END', {'variable': {}}, lambda value: 'VAR', 'VAREND'),
]


@pytest.mark.parametrize('template,context,serializer,expected', CUSTOM_SERIALIZER_CASES)
def test_custom_serializer(template, context, serializer, expected):
    assert render(template, context, serializer=serializer) == expected
