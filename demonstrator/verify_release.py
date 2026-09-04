from __future__ import annotations
import hashlib, json, os, subprocess, sys
from pathlib import Path

R=Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify_manifest():
    manifest=R/'SHA256SUMS.txt'
    checked=0
    for raw in manifest.read_text(encoding='utf-8').splitlines():
        if not raw.strip():
            continue
        digest, rel=raw.split('  ',1)
        p=R/rel
        if not p.is_file():
            raise SystemExit(f'MISSING_FILE: {rel}')
        actual=sha256(p)
        if actual!=digest:
            raise SystemExit(f'HASH_MISMATCH: {rel}: expected {digest}, got {actual}')
        checked+=1
    return checked

def run_script(name: str):
    cp=subprocess.run([sys.executable,str(R/name)],cwd=R,text=True,capture_output=True,timeout=180)
    if cp.returncode!=0:
        raise SystemExit(f'{name} FAIL\n{cp.stdout}\n{cp.stderr}')
    return json.loads(cp.stdout)

def main():
    import server
    checked=verify_manifest()
    server.ensure_runtime()

    live=[]
    for row in server.CONFIG['cases']:
        out=server.run_case(row['id'])
        if not out['replay_matches_reference']:
            raise SystemExit(f"REFERENCE_MISMATCH: {row['id']}")
        live.append({
            'case':row['id'],
            'claim_state':out['presentation']['claim_state'],
            'decision':out['presentation']['decision'],
        })

    custom=run_script('verify_custom.py')
    reviewer=run_script('verify_reviewer.py')
    result={
        'status':'PASS',
        'demo_version':server.CONFIG['demo_version'],
        'manifest_files_verified':checked,
        'live_preset_replay':f"{len(live)}/{len(server.CONFIG['cases'])}",
        'custom_regression':custom.get('status'),
        'reviewer_ab':reviewer.get('status'),
        'wheel_sha256':server.EXPECTED_WHEEL,
        'engine_sha256':server.EXPECTED_ENGINE,
        'python':sys.version.split()[0],
        'pip_required':False,
        'network_required':False,
        'live_results':live,
    }
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
