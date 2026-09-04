from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

R=Path(__file__).resolve().parent
C=json.loads((R/'demo_config.json').read_text())
EX=C['reviewer_experiment']
ENV=os.environ.copy(); ENV['PYTHONPATH']=str(R/'runtime'/'site')

def run(payload):
    cp=subprocess.run([sys.executable,str(R/'custom_case_runner.py')],input=json.dumps(payload),text=True,capture_output=True,env=ENV,timeout=30)
    if cp.returncode!=0:
        raise SystemExit(cp.stdout or cp.stderr)
    return json.loads(cp.stdout)

def main():
    import server
    server.ensure_runtime()
    a=EX['a']['input']; b=EX['b']['input']; changed=EX['changed_field']
    keys=set(a)|set(b)
    changed_keys=[k for k in keys if a.get(k)!=b.get(k)]
    if changed_keys!=[changed]:
        raise SystemExit(f'Experiment is not one-variable A/B: changed={changed_keys!r}, declared={changed!r}')
    ra,rb=run(a),run(b)
    ca=(ra.get('claim_states') or [{}])[0].get('status')
    cb=(rb.get('claim_states') or [{}])[0].get('status')
    ok=(ra.get('engine_sha256')==server.EXPECTED_ENGINE==rb.get('engine_sha256') and
        ra.get('control_closure') is False and rb.get('control_closure') is True and
        ca=='SUPPORTED' and cb=='VERIFIED')
    out={
        'status':'PASS' if ok else 'FAIL',
        'experiment_id':EX['id'],
        'only_changed_field':changed,
        'a':{'value':a[changed],'claim_state':ca,'control_closure':ra.get('control_closure')},
        'b':{'value':b[changed],'claim_state':cb,'control_closure':rb.get('control_closure')},
        'engine_sha256':server.EXPECTED_ENGINE,
    }
    print(json.dumps(out,indent=2))
    if not ok: raise SystemExit(1)

if __name__=='__main__': main()
