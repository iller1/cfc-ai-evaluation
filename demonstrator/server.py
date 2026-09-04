from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT/'demo_config.json').read_text(encoding='utf-8'))
WHEEL=ROOT/'cfc_anchor-0.2.90rc1-py3-none-any.whl'
EXPECTED_WHEEL=CONFIG['wheel_sha256']
EXPECTED_ENGINE=CONFIG['engine_sha256']
RUNTIME=ROOT/'runtime'/'site'
CUSTOM_SCHEMA=json.loads((ROOT/'custom_schema.json').read_text(encoding='utf-8'))

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ensure_runtime():
    if sys.version_info < (3,10):
        raise RuntimeError('Python 3.10 or newer is required')
    if sha256(WHEEL)!=EXPECTED_WHEEL:
        raise RuntimeError('Frozen wheel SHA-256 mismatch')
    marker=RUNTIME/'.ready'
    if marker.exists() and marker.read_text().strip()==EXPECTED_WHEEL:
        return
    if RUNTIME.exists(): shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True)
    # The wheel is already pinned by SHA-256. Extract it with Python's standard
    # library instead of invoking pip; this keeps the demo dependency-free while
    # giving the frozen engine a real filesystem path for its own identity hash.
    with zipfile.ZipFile(WHEEL) as zf:
        for info in zf.infolist():
            rel=Path(info.filename)
            if rel.is_absolute() or '..' in rel.parts:
                raise RuntimeError('Unsafe path in frozen wheel')
        zf.extractall(RUNTIME)
    marker.write_text(EXPECTED_WHEEL+'\n')

def case_row(case_id):
    return next((x for x in CONFIG['cases'] if x['id']==case_id),None)

def presentation(result):
    claims=result.get('claim_states') or []
    claim=claims[0] if claims else {}
    false_gates=[k for k,v in (result.get('gates') or {}).items() if v is False]
    closure=bool(result.get('control_closure'))
    if closure:
        reason=claim.get('reason') or 'Closure established by frozen controller.'
    elif claim.get('status') in {'UNRESOLVED','QUARANTINED'}:
        reason=claim.get('reason') or 'Closure not established.'
    elif false_gates:
        reason='Closure blocked by gate: '+', '.join(false_gates)
    else:
        reason='Closure not established by frozen controller.'
    return {'claim_state':claim.get('status'),'decision':'ALLOW' if closure else 'STOP','reason':reason,'false_gates':false_gates}

def run_custom(payload):
    ensure_runtime()
    script=ROOT/'custom_case_runner.py'
    env=os.environ.copy(); env['PYTHONPATH']=str(RUNTIME)
    cp=subprocess.run([sys.executable,str(script)],input=json.dumps(payload),env=env,capture_output=True,text=True,timeout=30)
    try:
        result=json.loads(cp.stdout)
    except Exception:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or f'custom runner exited {cp.returncode}')
    if cp.returncode!=0 or result.get('error'):
        raise ValueError(result.get('error') or cp.stderr.strip() or f'custom runner exited {cp.returncode}')
    if result.get('engine_sha256')!=EXPECTED_ENGINE:
        raise RuntimeError('Executed engine SHA-256 mismatch')
    return {'case_id':'CUSTOM_CASE','presentation':presentation(result),'result':result}

def run_case(case_id):
    row=case_row(case_id)
    if not row: raise KeyError(case_id)
    ensure_runtime()
    script=ROOT/'cases'/case_id/'run_case.py'
    env=os.environ.copy(); env['PYTHONPATH']=str(RUNTIME)
    cp=subprocess.run([sys.executable,str(script)],env=env,capture_output=True,text=True,timeout=30)
    if cp.returncode!=0:
        raise RuntimeError(cp.stderr.strip() or f'case runner exited {cp.returncode}')
    result=json.loads(cp.stdout)
    if result.get('engine_sha256')!=EXPECTED_ENGINE:
        raise RuntimeError('Executed engine SHA-256 mismatch')
    ref=json.loads((ROOT/'cases'/case_id/'reference_execution.json').read_text())
    raw=json.dumps(result,sort_keys=True,separators=(',',':'))
    raw_ref=json.dumps(ref,sort_keys=True,separators=(',',':'))
    return {'case_id':case_id,'replay_matches_reference':raw==raw_ref,'presentation':presentation(result),'result':result}

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=urlparse(path).path
        if path=='/': path='/index.html'
        return str(ROOT/path.lstrip('/'))
    def send_json(self,obj,status=200):
        data=json.dumps(obj,ensure_ascii=False,indent=2).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/status':
            ok=sha256(WHEEL)==EXPECTED_WHEEL
            self.send_json({'demo_version':CONFIG['demo_version'],'wheel_integrity':ok,'wheel_sha256':sha256(WHEEL),'expected_wheel_sha256':EXPECTED_WHEEL,'engine_sha256':EXPECTED_ENGINE,'public_api_contract_sha256':CONFIG.get('public_api_contract_sha256'),'reviewer_60s_path':CONFIG.get('reviewer_60s_path',[]),'reviewer_experiment':CONFIG.get('reviewer_experiment'),'mandatory_gates':CONFIG.get('mandatory_gates'),'persistence_schema':CONFIG.get('persistence_schema'),'cases':len(CONFIG['cases'])}); return
        if p=='/api/cases': self.send_json(CONFIG['cases']); return
        if p=='/api/custom/schema': self.send_json(CUSTOM_SCHEMA); return
        super().do_GET()
    def do_POST(self):
        p=urlparse(self.path).path
        if p=='/api/custom':
            try:
                n=int(self.headers.get('Content-Length','0'))
                if n<=0 or n>20000: raise ValueError('invalid request size')
                payload=json.loads(self.rfile.read(n).decode('utf-8'))
                self.send_json(run_custom(payload))
            except ValueError as e:self.send_json({'error':str(e)},400)
            except Exception as e:self.send_json({'error':str(e)},500)
            return
        if p.startswith('/api/run/'):
            cid=p.split('/api/run/',1)[1]
            try:self.send_json(run_case(cid))
            except KeyError:self.send_json({'error':'unknown case'},404)
            except Exception as e:self.send_json({'error':str(e)},500)
            return
        self.send_json({'error':'not found'},404)
    def log_message(self,fmt,*args):
        print('[demo]',fmt%args)

if __name__=='__main__':
    ensure_runtime()
    host=os.environ.get('CFC_DEMO_HOST','127.0.0.1'); port=int(os.environ.get('CFC_DEMO_PORT','8765'))
    print(f'CFC Demonstrator: http://{host}:{port}')
    ThreadingHTTPServer((host,port),Handler).serve_forever()
