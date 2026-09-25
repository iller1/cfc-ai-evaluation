from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import sys
from pathlib import Path

import server

ROOT = Path(__file__).resolve().parent
UX = json.loads((ROOT / 'ux_config_v1_1.json').read_text(encoding='utf-8'))
CONFIG = server.CONFIG
EXPECTED_PATH = [
    'CASE_01_UNRESOLVED_POSITIVE',
    'CASE_03_ACTIVE_CONFLICT_NO_RESOLUTION',
    'CASE_09_INACTIVE_UNBOUND_RESOLUTION',
    'CASE_10_INCOMPLETE_REQUIRED_CHECKS',
    'CASE_07_VALID_POSITIVE_CLOSURE',
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, ok: bool) -> None:
    print(f'{name}:', 'PASS' if ok else 'FAIL')
    if not ok:
        raise SystemExit(1)


def main() -> None:
    check('ux_version', UX.get('version') == '1.1-candidate')
    check('ux_path_exact', UX.get('path') == EXPECTED_PATH)
    check('path_matches_frozen_demo_config', CONFIG.get('reviewer_60s_path') == EXPECTED_PATH)
    check('five_human_explanations', all(UX.get('human_explanations', {}).get(x) for x in EXPECTED_PATH))
    check('full_v1_0_ui_preserved', (ROOT / 'index.html').is_file())
    check('reviewer_landing_present', (ROOT / 'review_60s.html').is_file())
    check('server_default_is_review_path', "if path=='/': path='/review_60s.html'" in (ROOT / 'server.py').read_text(encoding='utf-8'))
    check('frozen_wheel_identity', sha256(server.WHEEL) == CONFIG['wheel_sha256'])

    py_compile.compile(str(ROOT / 'server.py'), doraise=True)
    py_compile.compile(str(ROOT / 'demo_cli.py'), doraise=True)
    check('python_compile', True)

    cases = {x['id']: x for x in CONFIG['cases']}
    live_pass = 0
    for case_id in EXPECTED_PATH:
        result = server.run_case(case_id)
        expected_decision = cases[case_id]['closure_decision']
        actual_decision = result['presentation']['decision']
        ok = result['replay_matches_reference'] and actual_decision == expected_decision
        print(case_id, actual_decision, 'REFERENCE_MATCH' if result['replay_matches_reference'] else 'REFERENCE_MISMATCH', 'PASS' if ok else 'FAIL')
        live_pass += int(ok)
    check('five_live_replays', live_pass == len(EXPECTED_PATH))

    cp = subprocess.run([sys.executable, str(ROOT / 'demo_cli.py')], cwd=ROOT, capture_output=True, text=True, timeout=180)
    print(cp.stdout)
    if cp.stderr:
        print(cp.stderr, file=sys.stderr)
    check('demo_cli', cp.returncode == 0 and 'Review complete.' in cp.stdout)

    print('RESULT: CFC Demonstrator v1.1 UX candidate validation PASS')


if __name__ == '__main__':
    main()
