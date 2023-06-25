import json
from pathlib import Path
import pytest
from moosetash import render

SPECS_DIR = Path(__file__).parent.parent / 'spec' / 'specs'
TESTS = []

MUSTACHE_5_FEATURES = ['lambdas']

for spec_file in SPECS_DIR.glob('*.json'):
    if spec_file.name[0] == '~':
        if spec_file.name not in [f'~{name}.json' for name in MUSTACHE_5_FEATURES]:
            continue

    with open(spec_file, 'r') as file:
        spec_data = json.load(file)
        if 'tests' in spec_data:
            TESTS += [{**test, 'file': spec_file.stem} for test in spec_data['tests']]


def idfn(val):
    return '{file}.{name}'.format(**val).replace(' ', '_').replace('(', '[').replace(')', ']')


def parse_code(context):
    if isinstance(context, dict):
        if context.get('__tag__') == 'code':
            return eval(context['python'])
        return {key: parse_code(val) for key, val in context.items()}

    if isinstance(context, list):
        return [parse_code(val) for val in context]

    return context


@pytest.fixture(autouse=True, scope='function')
def clear_globals():
    if 'calls' in globals():
        del globals()['calls']


@pytest.mark.parametrize('test_data', TESTS, ids=idfn)
def test_spec(test_data):
    print(test_data['name'])
    print(test_data['desc'])

    assert (
        render(
            test_data['template'], parse_code(test_data['data']), partials=test_data.get('partials')
        )
        == test_data['expected']
    )


@pytest.mark.parametrize('test_data', TESTS, ids=idfn)
def test_spec_cached(test_data):
    print(test_data['name'])
    print(test_data['desc'])

    assert (
        render(
            test_data['template'],
            parse_code(test_data['data']),
            partials=test_data.get('partials'),
            cache_tokens=True,
        )
        == test_data['expected']
    )
