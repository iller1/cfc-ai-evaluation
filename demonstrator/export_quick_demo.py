"""Export the existing frozen-engine A/B experiment as a browser-only replay."""
import datetime
import json
from pathlib import Path
import subprocess
import server

ROOT = Path(__file__).resolve().parent

def main():
    experiment = server.CONFIG['reviewer_experiment']
    a, b = experiment['a']['input'], experiment['b']['input']
    assert [k for k in a.keys() | b.keys() if a.get(k) != b.get(k)] == ['independence_authority']
    results = {key: server.run_custom(experiment[key]['input']) for key in ('a', 'b')}
    assert results['a']['result']['control_closure'] is False
    assert results['b']['result']['control_closure'] is True
    assert results['a']['presentation']['claim_state'] == 'SUPPORTED'
    assert results['b']['presentation']['claim_state'] == 'VERIFIED'
    record = {
        'mode': 'recorded_frozen_engine_execution',
        'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'engine_sha256': server.EXPECTED_ENGINE,
        'wheel_sha256': server.EXPECTED_WHEEL,
        'experiment': experiment,
        'runs': results,
    }
    target = ROOT / 'quick'
    target.mkdir(exist_ok=True)
    (target / 'recorded-ab.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Exported two checked frozen-engine executions to quick/recorded-ab.json')

if __name__ == '__main__':
    main()
