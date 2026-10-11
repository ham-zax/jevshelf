"""Local TypeSafe credential bridge tests; never require or expose real API keys."""

import json
import os
import subprocess
from pathlib import Path


WRAPPER = Path(__file__).resolve().parents[1] / 'bin' / 'jevify-typesafe'


def helper_root(tmp_path):
    root = tmp_path / 'jevify'
    scripts = root / 'scripts'
    scripts.mkdir(parents=True)
    for name in ('scan', 'run_cases'):
        (scripts / f'{name}.py').write_text('''import json, os
print(json.dumps({"name": __file__.split("/")[-1],
                  "typesafe_set": bool(os.environ.get("TYPESAFE_API_KEY")),
                  "matches_expected": os.environ.get("TYPESAFE_API_KEY") == os.environ.get("EXPECTED_SYNTHETIC"),
                  "openrouter_set": bool(os.environ.get("OPENROUTER_API_KEY"))}))
''')
    return root


def test_maps_existing_jev_key_only_in_child_process(tmp_path):
    root = helper_root(tmp_path)
    env = dict(os.environ)
    env.pop('TYPESAFE_API_KEY', None)
    env['JEV_API_KEY'] = 'test-synthetic-jev-key'
    env['EXPECTED_SYNTHETIC'] = env['JEV_API_KEY']
    env['JEVIFY_SKILL_DIR'] = str(root)
    env.pop('OPENROUTER_API_KEY', None)
    process = subprocess.run(['bash', str(WRAPPER), 'scan'], env=env, capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    assert result == {'name': 'scan.py', 'typesafe_set': True, 'matches_expected': True, 'openrouter_set': False}
    assert 'test-synthetic-jev-key' not in process.stdout + process.stderr


def test_existing_typesafe_key_takes_priority(tmp_path):
    root = helper_root(tmp_path)
    env = dict(os.environ)
    env['TYPESAFE_API_KEY'] = 'test-synthetic-typesafe-key'
    env['JEV_API_KEY'] = 'test-other-key'
    env['EXPECTED_SYNTHETIC'] = 'test-synthetic-typesafe-key'
    env['JEVIFY_SKILL_DIR'] = str(root)
    process = subprocess.run(['bash', str(WRAPPER), 'run-cases'], env=env, capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout)['matches_expected']
    assert 'test-synthetic-typesafe-key' not in process.stdout + process.stderr
