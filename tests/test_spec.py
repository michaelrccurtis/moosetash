import json
from pathlib import Path
import pytest
from moosetash import render

SPECS_DIR = Path(__file__).parent.parent / 'spec' / 'specs'
TESTS = []

for spec_file in SPECS_DIR.glob('*.json'):
    if spec_file.name[0] == '~':
        continue

    with open(spec_file, 'r') as file:
        spec_data = json.load(file)
        if 'tests' in spec_data:
            TESTS += [{**test, 'file': spec_file.stem} for test in spec_data['tests']]


def idfn(val):
    return '{file}.{name}'.format(**val).replace(' ', '_').replace('(', '[').replace(')', ']')


@pytest.mark.parametrize('test_data', TESTS, ids=idfn)
def test_spec(test_data):
    print(test_data['name'])
    print(test_data['desc'])

    assert (
        render(test_data['template'], test_data['data'], partials=test_data.get('partials'))
        == test_data['expected']
    )


@pytest.mark.parametrize('test_data', TESTS, ids=idfn)
def test_spec_cached(test_data):
    print(test_data['name'])
    print(test_data['desc'])

    assert (
        render(
            test_data['template'],
            test_data['data'],
            partials=test_data.get('partials'),
            cache_tokens=True,
        )
        == test_data['expected']
    )
