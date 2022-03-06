import pytest
from moosetash import MissingVariable, missing_variable_keep, missing_variable_raise, render


def test_missing_variable_default():
    assert render('{{ variable }}', {}) == ''


def test_missing_variable_raise():
    with pytest.raises(MissingVariable, match='variable'):
        render('{{ variable }}', {}, missing_variable_handler=missing_variable_raise)


def test_missing_variable_keep():
    assert (
        render('{{ variable }}', {}, missing_variable_handler=missing_variable_keep)
        == '{{ variable }}'
    )


def test_missing_variable_keep_delims():
    assert (
        render('{{=| |=}}| variable |', {}, missing_variable_handler=missing_variable_keep)
        == '| variable |'
    )
