import hashlib,json,subprocess,sys,os
from pathlib import Path
R=Path(__file__).resolve().parent
C=json.loads((R/'demo_config.json').read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert h(R/'cfc_anchor-0.2.90rc1-py3-none-any.whl')==C['wheel_sha256']
for row in C['cases']:
    d=R/'cases'/row['id']
    v=json.loads((d/'VALIDATION.json').read_text()); assert v.get('status',v.get('result'))=='PASS'
print(json.dumps({'status':'PASS','cases':len(C['cases']),'wheel_sha256':C['wheel_sha256'],'engine_sha256':C['engine_sha256']},indent=2))
