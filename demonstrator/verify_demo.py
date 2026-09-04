from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
C=json.loads((R/'demo_config.json').read_text())
S=json.loads((R/'custom_schema.json').read_text())
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert h(R/'cfc_anchor-0.2.90rc1-py3-none-any.whl')==C['wheel_sha256']
assert C['engine_sha256']=='77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0'
assert len(C['cases'])==10
for row in C['cases']:
    d=R/'cases'/row['id']
    v=json.loads((d/'VALIDATION.json').read_text())
    assert v.get('status',v.get('result'))=='PASS'
assert S['schema_version']=='1'
assert (R/'custom_case_runner.py').is_file()
print(json.dumps({'status':'PASS','preset_cases':len(C['cases']),'custom_builder_schema':S['schema_version'],'wheel_sha256':C['wheel_sha256'],'engine_sha256':C['engine_sha256']},indent=2))
