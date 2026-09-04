from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parent
ENV=os.environ.copy(); ENV['PYTHONPATH']=str(R/'runtime'/'site')
CASES=[
    ('single_valid_positive', {'conclusion':'POSITIVE','required_independent_supports':1,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'}]}, 'VERIFIED', True),
    ('single_valid_negative', {'conclusion':'NEGATIVE','required_independent_supports':1,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'NEGATIVE','validity':'CURRENT'}]}, 'VERIFIED', True),
    ('active_conflict', {'conclusion':'POSITIVE','required_independent_supports':1,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'},{'polarity':'NEGATIVE','validity':'CURRENT'}]}, 'QUARANTINED', False),
    ('stale_support', {'conclusion':'POSITIVE','required_independent_supports':1,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'STALE'}]}, 'UNRESOLVED', False),
    ('wrong_scope', {'conclusion':'POSITIVE','required_independent_supports':1,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'WRONG','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'}]}, 'VERIFIED', False),
    ('one_of_two_required', {'conclusion':'POSITIVE','required_independent_supports':2,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'}]}, 'SUPPORTED', False),
    ('two_distinct_uncertified', {'conclusion':'POSITIVE','required_independent_supports':2,'provenance_shape':'DISTINCT','independence_authority':'NONE','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'},{'polarity':'POSITIVE','validity':'CURRENT'}]}, 'SUPPORTED', False),
    ('two_distinct_certified', {'conclusion':'POSITIVE','required_independent_supports':2,'provenance_shape':'DISTINCT','independence_authority':'VERIFIED','scope':'EXPECTED','evidence':[{'polarity':'POSITIVE','validity':'CURRENT'},{'polarity':'POSITIVE','validity':'CURRENT'}]}, 'VERIFIED', True),
]

def main():
    import server
    server.ensure_runtime()
    passed=0; rows=[]
    for name,payload,state,closure in CASES:
        cp=subprocess.run([sys.executable,str(R/'custom_case_runner.py')],input=json.dumps(payload),text=True,capture_output=True,env=ENV,timeout=30)
        if cp.returncode!=0: raise SystemExit(f'{name}: runner failed: {cp.stdout or cp.stderr}')
        r=json.loads(cp.stdout); claim=(r.get('claim_states') or [{}])[0].get('status')
        ok=(claim==state and r.get('control_closure') is closure and r.get('engine_sha256')==server.EXPECTED_ENGINE)
        rows.append({'case':name,'claim_state':claim,'control_closure':r.get('control_closure'),'expected_state':state,'expected_closure':closure,'pass':ok})
        if not ok: raise SystemExit(json.dumps(rows,indent=2))
        passed+=1
    print(json.dumps({'status':'PASS','custom_cases':passed,'engine_sha256':server.EXPECTED_ENGINE,'results':rows},indent=2))
if __name__=='__main__': main()
