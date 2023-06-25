"""Run benchmark suite against different python libraries"""

from typing import Any
import difflib
import json
from pathlib import Path
from timeit import timeit
import chevron
import moosetash

DEFAULT_SAMPLES = 10000
BENCHMARK_FOLDER = Path(__file__).parent / 'templates'


def moosetash_test(template: str, context: Any):
    """Basic moostash rendering"""
    return moosetash.render(template, context)


def moosetash_test_fast(template: str, context: Any):
    """Fast moostash rendering"""
    return moosetash.render(template, context, cache_tokens=True)


def chevron_test(template: str, context: Any):
    """Chevron rendering"""
    return chevron.render(template, context)


TESTS = [
    ('Moostash', moosetash_test),
    ('Moostash [Tokens Cached]', moosetash_test_fast),
    ('Chevron', chevron_test),
]


def get_benchmarks():
    benchmarks = []
    for file in BENCHMARK_FOLDER.glob('*.mustache'):
        with open(file, 'r') as template_file:
            template = template_file.read()

        context_file_path = BENCHMARK_FOLDER / f'{file.stem}.json'
        output_file_path = BENCHMARK_FOLDER / f'{file.stem}.txt'

        context = {}
        if context_file_path.is_file():
            with open(context_file_path, 'r') as context_file:
                context = json.load(context_file)

        if not output_file_path.is_file():
            raise FileNotFoundError(f'No output file found at {output_file_path}')
        with open(output_file_path, 'r') as output_file:
            output = output_file.read()

        benchmarks.append((file.stem, template, context, output))
    return benchmarks


def run_benchmarks(samples: int):
    """Run the benchmark suite for each library"""

    max_lib_name = max(len(name) for name, _ in TESTS)
    for name, template, context, expected in get_benchmarks():
        print(f'Benchmark {name}:')
        for lib_name, test_func in TESTS:
            print(f'\t{lib_name}:', end='', flush=True)

            def test(
                test_func=test_func,
                template=template,
                context=context,
                expected=expected,
                lib_name=lib_name,
                name=name,
            ):
                rendered = test_func(template, context)
                if rendered != expected:
                    print(repr(rendered))
                    print(repr(expected))
                    raw_diff = difflib.Differ().compare(
                        expected.splitlines(), rendered.splitlines()
                    )
                    content_diff = [
                        item for item in raw_diff if item and item[0] in ['-', '+', '?']
                    ]
                    for line in content_diff:
                        print(line)
                    raise ValueError(f'Unexpected output from lib {lib_name} for benchmark {name}')

            time = timeit(test, number=samples)

            print(' ' * (max_lib_name - len(lib_name)), 'Time:', round(time, 3))


def run():
    """Run all the benchmarks against all the libraries"""
    run_benchmarks(DEFAULT_SAMPLES)
