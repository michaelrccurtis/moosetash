import pytest
from moosetash.tokenizer import Token, find_next_pointer, find_next_tag, parse_tag, tokenize

FIND_NEXT_TAG_CASES = [
    (('PRETAGSTRING{{ }}', 0, '{{'), ('PRETAGSTRING', 12)),
    (('PRETAGSTRING[[ ]]', 0, '[['), ('PRETAGSTRING', 12)),
    (('PRETAGSTRING[[ ]]', 0, '{{'), ('PRETAGSTRING[[ ]]', 17)),
]


@pytest.mark.parametrize('test_input,expected', FIND_NEXT_TAG_CASES)
def test_find_next_tag(test_input, expected):
    assert find_next_tag(*test_input) == expected


NEXT_POINTER_CASES = [
    (('{{ variable }}', 0, 14), (True, 14, 0)),
]


@pytest.mark.parametrize('test_input,expected', NEXT_POINTER_CASES)
def test_find_next_pointer(test_input, expected):
    assert find_next_pointer(*test_input) == expected


TOKENIZE_CASES = [
    (('{{ variable }}', 0, '{{', '}}'), [((Token.VARIABLE, 'variable', ''), 14)]),
    (
        ('{{# section }}{{/ section }}', 0, '{{', '}}'),
        [((Token.SECTION, 'section', ''), 14), ((Token.END, 'section', ''), 28)],
    ),
    (
        ('{{# section }}{{ variable }}{{/ section }}', 0, '{{', '}}'),
        [
            ((Token.SECTION, 'section', ''), 14),
            ((Token.VARIABLE, 'variable', ''), 28),
            ((Token.END, 'section', ''), 42),
        ],
    ),
    (
        ('{{# section }} A literal string {{/ section }}', 0, '{{', '}}'),
        [
            ((Token.SECTION, 'section', ''), 14),
            ((Token.LITERAL, ' A literal string ', ''), 32),
            ((Token.END, 'section', ''), 46),
        ],
    ),
    (
        ('{{# section }} \nA literal string\n {{/ section }}', 0, '{{', '}}'),
        [
            ((Token.SECTION, 'section', ''), 16),
            ((Token.LITERAL, 'A literal string\n', ''), 34),
            ((Token.END, 'section', ''), 48),
        ],
    ),
]


@pytest.mark.parametrize('test_input,expected', TOKENIZE_CASES)
def test_tokenizer(test_input, expected):
    assert list(tokenize(*test_input)) == expected


def test_tokenizer_generator():
    expected_tokens = [
        ((Token.VARIABLE, 'variable', ''), 14),
        ((Token.LITERAL, ' LITERAL', ''), 22),
    ]
    count = 0
    for token in tokenize('{{ variable }} LITERAL'):
        assert token == expected_tokens[count]
        count += 1


PARSE_TAG_CASES = [
    (('{{ variable }}', 0, '{{', '}}'), ((Token.VARIABLE, 'variable'), 14)),
    (('{{! different.variable }}', 0, '{{', '}}'), ((Token.COMMENT, 'different.variable'), 25)),
    (('{{# variable_name }}', 0, '{{', '}}'), ((Token.SECTION, 'variable_name'), 20)),
    (('{{^ value }}', 0, '{{', '}}'), ((Token.INVERTED, 'value'), 12)),
    (('{{/ section }}', 0, '{{', '}}'), ((Token.END, 'section'), 14)),
    (('{{> some_name{ }}', 0, '{{', '}}'), ((Token.PARTIAL, 'some_name{'), 17)),
    (('{{= start end =}}', 0, '{{', '}}'), ((Token.SET_DELIMITER, 'start end'), 17)),
    (('{{{ <html></html> }}}', 0, '{{', '}}'), ((Token.NO_ESCAPE, '<html></html>'), 21)),
    (('{{& <img /> }}', 0, '{{', '}}'), ((Token.NO_ESCAPE, '<img />'), 14)),
    (
        ('{{ variable }}{{! different.variable }}', 0, '{{', '}}'),
        ((Token.VARIABLE, 'variable'), 14),
    ),
    (
        ('{{ variable }}{{! different.variable }}', 14, '{{', '}}'),
        ((Token.COMMENT, 'different.variable'), 39),
    ),
]


@pytest.mark.parametrize('test_input,expected', PARSE_TAG_CASES)
def test_parse_tag(test_input, expected):
    assert parse_tag(*test_input) == expected
