#!/usr/bin/env python3
"""Run frozen mechanical tests against temporary, wholly synthetic assets."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    report = Path(__file__).resolve().parent
    names = ('build_counts.py', 'finite_model.py', 'run_experiment.py',
             'test_mechanical.py', 'test_phase_api.py')
    with tempfile.TemporaryDirectory(prefix='anna-mechanical-fixtures-') as directory:
        temporary = Path(directory)
        case = temporary / 'case'
        code = case / 'code'
        assets = case / 'assets'
        code.mkdir(parents=True)
        assets.mkdir()
        for name in names:
            shutil.copyfile(report / 'code' / name, code / name)
        text = assets / 'listy_I.txt'
        text.write_text('ab!ch a', encoding='utf-8')
        specification = importlib.util.spec_from_file_location(
            'synthetic_fixture_count_builder', code / 'build_counts.py')
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        module.build(text, assets / 'counts.npz')
        descriptor = temporary / 'key-foundation-audit-next-20261013'
        descriptor.mkdir()
        (descriptor / 'one-practical-rebuild-test-v1.json').write_text(
            json.dumps({'schema': 'synthetic-mechanical-provenance-fixture-v1',
                        'scientific_experiment_descriptor': False,
                        'purpose': 'Temporary dependency for phase API fixtures only'}) + '\n',
            encoding='utf-8')
        subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', str(code),
             '-p', 'test_*.py', '-v'], cwd=case, check=True)


if __name__ == '__main__':
    main()
