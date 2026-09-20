from __future__ import annotations
import json, os, sys, threading, time, uuid
from dataclasses import dataclass, field
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demonstrator"
sys.path.insert(0, str(DEMO))
import server as cfc_demo

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
SESSION_COOKIE = "CFC_HAWM_WEB_SID"
SESSION_TTL = 4 * 60 * 60

MODES = {
    "YES_NO": "If the user asks a yes/no or proposition-status question, the first line must be exactly one of: YES, NO, NOT ENOUGH INFORMATION YET, followed by at most one short sentence. If the message is a greeting, command, open-ended request, or otherwise not suitable for that tri-state contract, answer normally in one short sentence without adding a tri-state label. Do not pretend certainty.",
    "MINIMUM": "Answer briefly and directly. Use at most a few sentences.",
    "STANDARD": "Answer clearly, directly, and at a normal level of detail.",
    "EXPANDED": "Answer in more detail, including reasoning, limitations, and relevant details.",
}

@dataclass
class Session:
    sid: str
    created: float = field(default_factory=time.time)
    seen: float = field(default_factory=time.time)
    provider: str | None = None
    model: str = "gemini-3.8-flash"
    api_key: str | None = None
    mode: str = "STANDARD"
    history: list[dict] = field(default_factory=list)
    hawm: dict = field(default_factory=lambda: {
        "GOAL": "Help the user with the current conversation without inventing missing information.",
        "CURRENT_TASK": "",
        "CURRENT_BRANCH": "main",
        "CLAIMS": [],
        "EVIDENCE": [],
        "CONSTRAINTS": ["Do not turn UNRESOLVED into TRUE/FALSE without sufficient basis."],
        "DECISIONS": [],
        "UNRESOLVED": [],
        "NEXT_ACTION": "",
        "LAST_VERIFIED_STATE": "session_created",
    })

SESSIONS: dict[str, Session] = {}
LOCK = threading.RLock()

def cleanup():
    now = time.time()
    with LOCK:
        for sid in list(SESSIONS):
            if now - SESSIONS[sid].seen > SESSION_TTL:
                SESSIONS[sid].api_key = None
                del SESSIONS[sid]

def new_session():
    s = Session(uuid.uuid4().hex + uuid.uuid4().hex)
    with LOCK:
        SESSIONS[s.sid] = s
    return s

def get_session(sid):
    cleanup()
    if not sid:
        return None
    with LOCK:
        s = SESSIONS.get(sid)
        if s:
            s.seen = time.time()
        return s

def gemini_call(s: Session, text: str):
    if not s.api_key:
        raise RuntimeError("API_KEY_REQUIRED")
    model = s.model or "gemini-3.8-flash"
    system = (
        "You are the model inside a CFC+HAWM public evaluation chat. "
        "The ordinary natural-language reply is NOT CFC-authorized. "
        "Respect the following HAWM state and do not invent missing evidence.\n\n"
        + json.dumps(s.hawm, ensure_ascii=False)
        + "\n\n"
        + MODES.get(s.mode, MODES["STANDARD"])
    )
    contents = []
    for row in s.history[-20:]:
        role = "model" if row["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": row["content"]}]})
    contents.append({"role": "user", "parts": [{"text": text}]})
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": {"YES_NO":256,"MINIMUM":384,"STANDARD":768,"EXPANDED":1536}[s.mode]}
    }).encode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model)}:generateContent?key={quote(s.api_key)}"
    req = Request(url, data=body, headers={"Content-Type":"application/json"}, method="POST")
    data = None
    for attempt, delay in enumerate((0, 1.5, 4.0)):
        if delay:
            time.sleep(delay)
        try:
            with urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except HTTPError as e:
            code = int(getattr(e, "code", 0) or 0)
            if code in {500, 502, 503, 504} and attempt < 2:
                continue
            if code == 429:
                raise RuntimeError("Gemini rate limit reached. Please try again shortly or check your API quota.")
            if code == 503:
                raise RuntimeError("Gemini is temporarily unavailable (503). Please try again in a moment.")
            raise RuntimeError(f"Gemini API returned HTTP {code}.")
        except URLError:
            if attempt < 2:
                continue
            raise RuntimeError("Could not reach Gemini. Please check your connection and try again.")
    if data is None:
        raise RuntimeError("Gemini is temporarily unavailable. Please try again.")
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        raise RuntimeError("Gemini returned an empty response. Please try again.")

INDEX = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CFC + HAWM</title>
<style>
:root{font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;color:#172033;background:#f5f7fb}
*{box-sizing:border-box} body{margin:0}.wrap{max-width:980px;margin:auto;padding:18px}.top{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{font-size:22px;margin:0}.tag{font-size:12px;background:#e8eefc;padding:6px 9px;border-radius:999px}.modes{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0}
button{border:0;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:650;background:#e7ebf3;color:#182033}
button.active,button.primary{background:#2457ff;color:white}.chat{background:white;border:1px solid #dfe5ef;border-radius:16px;min-height:440px;padding:18px;box-shadow:0 8px 28px #20305010}
.msg{max-width:82%;padding:11px 13px;border-radius:14px;margin:9px 0;white-space:pre-wrap;line-height:1.42}.u{margin-left:auto;background:#2457ff;color:white}.a{background:#f0f3f8}.meta{font-size:11px;opacity:.7;margin-top:6px}
.entry{display:flex;gap:8px;margin-top:12px}.entry textarea{flex:1;resize:vertical;min-height:58px;border:1px solid #cfd7e5;border-radius:12px;padding:12px;font:inherit}
.panel{margin-top:14px;background:white;border:1px solid #dfe5ef;border-radius:14px;padding:14px}.hidden{display:none}.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input,select{padding:9px 10px;border:1px solid #cfd7e5;border-radius:9px}.status{font-size:12px;margin-top:8px}.warn{background:#fff7dd;border:1px solid #f1df9b;padding:10px;border-radius:10px;margin:10px 0}.ok{background:#eaf8ee;border:1px solid #bde2c7;padding:10px;border-radius:10px;margin:10px 0}
pre{white-space:pre-wrap;background:#111827;color:#e5e7eb;padding:12px;border-radius:10px;overflow:auto}
</style></head><body><div class="wrap">
<div class="top"><h1>CFC + HAWM</h1><span class="tag">Public Web Alpha</span></div>
<div class="modes">
<button data-mode="YES_NO">YES / NO</button><button data-mode="MINIMUM">MINIMUM</button><button data-mode="STANDARD" class="active">STANDARD</button><button data-mode="EXPANDED">EXPANDED</button>
</div>
<div class="chat" id="chat"><div class="a msg">Welcome. This is the public CFC + HAWM chat. Ordinary conversation remains <b>MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2</b>. To use ordinary chat, connect your own Gemini API key in Options. The prepared CFC example works separately through the frozen controller.</div></div>
<div class="entry"><textarea id="text" placeholder="Type a message..."></textarea><button class="primary" id="send">Send</button></div>
<div class="row" style="margin-top:10px"><button id="new">New chat</button><button id="cfc">Run prepared CFC example</button><button id="opts">Options and technical details</button></div>
<div class="panel hidden" id="panel">
<div class="row"><select id="provider"><option value="gemini">Gemini</option></select><input id="model" value="gemini-3.8-flash"><input id="key" type="password" placeholder="Gemini API key"><button id="connect">Connect model</button><button id="getkey" type="button">Get Gemini API key</button></div>
<div class="status" id="status">The API key is kept in this browser tab's session storage and in server memory while connected. It is not written to application files.</div>
<div class="warn"><b>Boundary:</b> ordinary model replies are not automatically authorized by CFC. The prepared CFC example is a separate structured path.</div>
<pre id="tech">Loading...</pre>
</div>
</div>
<script>
let mode="STANDARD";
const q=s=>document.querySelector(s), chat=q("#chat");
function add(role,text,meta=""){const d=document.createElement("div");d.className="msg "+(role==="user"?"u":"a");d.textContent=text;if(meta){const m=document.createElement("div");m.className="meta";m.textContent=meta;d.appendChild(m)}chat.appendChild(d);chat.scrollTop=chat.scrollHeight}
async function api(path,opt={}){const r=await fetch(path,{headers:{"Content-Type":"application/json"},...opt});const j=await r.json();if(!r.ok)throw new Error(j.error||j.code||r.status);return j}
document.querySelectorAll("[data-mode]").forEach(b=>b.onclick=()=>{mode=b.dataset.mode;document.querySelectorAll("[data-mode]").forEach(x=>x.classList.remove("active"));b.classList.add("active")});
async function reconnectStoredKey(){
  const key=sessionStorage.getItem("cfc_hawm_gemini_key");
  if(!key)return false;
  const provider=sessionStorage.getItem("cfc_hawm_provider")||"gemini";
  const modelName=sessionStorage.getItem("cfc_hawm_model")||q("#model").value||"gemini-3.8-flash";
  await api("/api/connect",{method:"POST",body:JSON.stringify({provider,model:modelName,api_key:key})});
  q("#status").textContent="Connected: "+provider+" / "+modelName+" — restored for this browser session.";
  return true;
}
async function sendChatMessage(t){
  try{
    const j=await api("/api/chat",{method:"POST",body:JSON.stringify({text:t,mode})});
    add("assistant",j.text,j.authority+" / CFC "+j.cfc_status);
  }catch(e){
    if(String(e.message).includes("API_KEY_REQUIRED")){
      try{
        if(await reconnectStoredKey()){
          const j=await api("/api/chat",{method:"POST",body:JSON.stringify({text:t,mode})});
          add("assistant",j.text,j.authority+" / CFC "+j.cfc_status);
          return;
        }
      }catch(reconnectError){
        sessionStorage.removeItem("cfc_hawm_gemini_key");
      }
      q("#panel").classList.remove("hidden");
      add("assistant","Gemini is not connected. Add your API key in Options to start chatting.");
    }else{
      add("assistant","Error: "+e.message);
    }
  }
}
q("#send").onclick=async()=>{const t=q("#text").value.trim();if(!t)return;q("#text").value="";add("user",t);await sendChatMessage(t)};
q("#connect").onclick=async()=>{try{const provider=q("#provider").value,modelName=q("#model").value,rawKey=q("#key").value;const j=await api("/api/connect",{method:"POST",body:JSON.stringify({provider,model:modelName,api_key:rawKey})});sessionStorage.setItem("cfc_hawm_gemini_key",rawKey);sessionStorage.setItem("cfc_hawm_provider",j.provider);sessionStorage.setItem("cfc_hawm_model",j.model);q("#key").value="";q("#status").textContent="Connected: "+j.provider+" / "+j.model+" — key available for new chats in this browser tab."}catch(e){q("#status").textContent="Error: "+e.message}};q("#getkey").onclick=()=>window.open("https://aistudio.google.com/app/apikey","_blank","noopener,noreferrer");
q("#cfc").onclick=async()=>{add("assistant","Running the frozen CFC example...");try{const j=await api("/api/cfc",{method:"POST",body:"{}"});add("assistant","CFC: "+j.presentation.claim_state+"\nDECISION: "+j.presentation.decision+"\nREASON: "+j.presentation.reason,"frozen cfc-anchor 0.2.90rc1")}catch(e){add("assistant","CFC error: "+e.message)}};
q("#new").onclick=async()=>{await api("/api/new",{method:"POST",body:"{}"});chat.innerHTML="";add("assistant","New chat started.")};
q("#opts").onclick=async()=>{q("#panel").classList.toggle("hidden");try{q("#tech").textContent=JSON.stringify(await api("/api/status"),null,2)}catch(e){q("#tech").textContent=e.message}};
q("#text").addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();q("#send").click()}});
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    server_version = "CFCHAWMHostedAlpha/1.0"
    def log_message(self, fmt, *args): print("[web]", fmt % args)
    def _sid(self):
        raw = self.headers.get("Cookie","")
        jar = cookies.SimpleCookie()
        try: jar.load(raw)
        except Exception: return None
        m = jar.get(SESSION_COOKIE)
        return m.value if m else None
    def _session(self):
        s = get_session(self._sid())
        self._set_cookie = False
        if not s:
            s = new_session(); self._set_cookie = True
        return s
    def _headers(self, ctype="application/json; charset=utf-8"):
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","no-referrer")
        if getattr(self,"_set_cookie",False):
            self.send_header("Set-Cookie",f"{SESSION_COOKIE}={self.s.sid}; Path=/; HttpOnly; SameSite=Lax; Secure; Max-Age={SESSION_TTL}")
    def _json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode("utf-8")
        self.send_response(status); self._headers(); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def _body(self):
        n=min(int(self.headers.get("Content-Length","0") or 0),1_000_000)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")
    def do_GET(self):
        self.s=self._session(); p=urlparse(self.path).path
        if p=="/healthz": self._json({"ok":True}); return
        if p=="/":
            raw=INDEX.encode("utf-8"); self.send_response(200); self._headers("text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if p=="/api/status":
            self._json({"authority":"MODEL_REPLY_UNCHECKED","cfc_status":"NOT_CONNECTED_C2","mode":self.s.mode,"provider":self.s.provider,"model":self.s.model,"history_messages":len(self.s.history),"hawm":self.s.hawm,"frozen_cfc":{"anchor":"0.2.90rc1","wheel_sha256":cfc_demo.EXPECTED_WHEEL,"engine_sha256":cfc_demo.EXPECTED_ENGINE}}); return
        self._json({"error":"NOT_FOUND"},404)
    def do_POST(self):
        self.s=self._session(); p=urlparse(self.path).path
        try:
            body=self._body()
            if p=="/api/connect":
                provider=str(body.get("provider") or "").lower(); model=str(body.get("model") or "").strip(); key=str(body.get("api_key") or "").strip()
                if provider!="gemini": raise ValueError("HOSTED_ALPHA_SUPPORTS_GEMINI_ONLY")
                if not model or not key: raise ValueError("MODEL_AND_API_KEY_REQUIRED")
                self.s.provider=provider; self.s.model=model; self.s.api_key=key
                self._json({"provider":provider,"model":model,"api_key_session_only":True}); return
            if p=="/api/chat":
                text=str(body.get("text") or "").strip(); mode=str(body.get("mode") or "STANDARD").upper()
                if not text: raise ValueError("TEXT_REQUIRED")
                if mode not in MODES: mode="STANDARD"
                self.s.mode=mode; self.s.hawm["CURRENT_TASK"]=text; self.s.hawm["NEXT_ACTION"]="answer_current_user_message"
                answer=gemini_call(self.s,text)
                self.s.history.append({"role":"user","content":text}); self.s.history.append({"role":"assistant","content":answer})
                self.s.hawm["LAST_VERIFIED_STATE"]="ordinary_model_reply_unchecked"
                self._json({"text":answer,"authority":"MODEL_REPLY_UNCHECKED","cfc_status":"NOT_CONNECTED_C2","mode":mode}); return
            if p=="/api/cfc":
                out=cfc_demo.run_case("CASE_01_UNRESOLVED_POSITIVE")
                self._json(out); return
            if p=="/api/new":
                self.s.history.clear(); self.s.hawm["CURRENT_TASK"]=""; self.s.hawm["NEXT_ACTION"]=""; self.s.hawm["LAST_VERIFIED_STATE"]="new_conversation"
                self._json({"ok":True}); return
            self._json({"error":"NOT_FOUND"},404)
        except Exception as e:
            self._json({"error":f"{type(e).__name__}: {e}"},400)

if __name__=="__main__":
    cfc_demo.ensure_runtime()
    print(f"CFC+HAWM Hosted Alpha listening on {HOST}:{PORT}")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
