"""DF-023M judge review (PRIVATE). Local-only, immutable-authority playback.

Only GET and 3 self-contained assets + manifest-gated synthetic evidence.
No Meta HTTP client, no credential input, no PDF import and no mutations.
"""
from __future__ import annotations
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
import argparse,json
import df023m_verify as verifier

ROOT=Path(__file__).resolve().parent
ASSETS={
 "/":("df023m_index.html","text/html; charset=utf-8"),
 "/index.html":("df023m_index.html","text/html; charset=utf-8"),
 "/df023m_style.css":("df023m_style.css","text/css; charset=utf-8"),
 "/df023m_ui.js":("df023m_ui.js","text/javascript; charset=utf-8"),
}
HEADERS={
 "Cache-Control":"no-store",
 "X-Frame-Options":"DENY",
 "X-Content-Type-Options":"nosniff",
 "Referrer-Policy":"no-referrer",
 "Cross-Origin-Resource-Policy":"same-origin",
 "Content-Security-Policy":"default-src 'none';script-src 'self';style-src 'self';connect-src 'self';img-src 'self' data:;base-uri 'none';form-action 'none';frame-ancestors 'none'",
}
class Viewer(BaseHTTPRequestHandler):
 server_version="TrueLanded-DF023M-JuryReplay"
 sys_version=""
 def log_message(self,*args):return
 def reply(self,status,body,mime="application/json; charset=utf-8"):
  if not isinstance(body,bytes):
   body=json.dumps(body,sort_keys=True,ensure_ascii=True).encode("utf8")
  if len(body)>150000:
   body=b'{"error":"OUTPUT_SIZE_REFUSED"}';status=503
  self.send_response(status)
  self.send_header("Content-Type",mime)
  self.send_header("Content-Length",str(len(body)))
  for k,v in HEADERS.items():self.send_header(k,v)
  self.end_headers()
  try:self.wfile.write(body)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_GET(self):
  allowed_hosts={f"127.0.0.1:{self.server.server_port}",
                 f"localhost:{self.server.server_port}"}
  host=self.headers.get("Host","")
  if (host not in allowed_hosts or
      self.headers.get("Origin","") not in ("",*[f"http://{x}" for x in allowed_hosts]) or
      self.headers.get("Cookie") or self.headers.get("Authorization") or
      self.headers.get("Sec-Fetch-Site")=="cross-site"):
   return self.reply(403,{"error":"LOCAL_SAME_ORIGIN_REQUIRED"})
  uri=urlsplit(self.path)
  if uri.query or uri.fragment:return self.reply(422,{"error":"NO_QUERY_SUPPORTED"})
  if uri.path in ASSETS:
   filename,mime=ASSETS[uri.path]
   p=ROOT/filename
   if not p.is_file() or p.is_symlink():
    return self.reply(503,{"error":"ASSET_MISSING"})
   return self.reply(200,p.read_bytes(),mime)
  if uri.path=="/api/scene":
   try:
    verdict=verifier.verify(ROOT)
    if verdict["gate"]!="DF023M_LOCAL_INTEGRITY_REPLAY_PASS":
     return self.reply(503,{"error":"SOURCE_GATE_REFUSED"})
    evidence=json.loads((ROOT/"DF023M_JURY_EVIDENCE.json").read_text("utf8"))
    manifest=json.loads((ROOT/verifier.MANIFEST).read_text("utf8"))
    verifier.source_valid(evidence)
    return self.reply(200,{"gate":"DF023M_SELF_CHECKED_LOCAL_REPLAY",
       "evidence":evidence,"manifest":{
        "public_release_approved":manifest["public_release_approved"],
        "redistribution_license_granted":manifest["redistribution_license_granted"],
        "source_git_commit_observed":manifest["source_git_commit_observed"]}})
   except Exception:
    # No paths, source contents or tracebacks leaked.
    return self.reply(503,{"error":"MANDATORY_LOCAL_INTEGRITY_FAILED"})
  return self.reply(404,{"error":"ROUTE_NOT_ALLOWLISTED"})
 def do_POST(self):self.reply(405,{"error":"READ_ONLY_NO_ACTIONS"})
 def do_PUT(self):self.do_POST()
 def do_DELETE(self):self.do_POST()
 def do_PATCH(self):self.do_POST()
 def do_OPTIONS(self):self.do_POST()
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--port",type=int,default=18970)
 args=parser.parse_args()
 if not 1024<=args.port<=65535:raise SystemExit("INVALID_LOCAL_PORT")
 with ThreadingHTTPServer(("127.0.0.1",args.port),Viewer) as http:
  print(f"DF023M_PRIVATE_JURY_REPLAY=http://127.0.0.1:{args.port}/",flush=True)
  print("MODE_LOCAL_DERIVED_REAL_META_REPLAY_NO_NETWORK_OR_KEYS",flush=True)
  http.serve_forever(poll_interval=.2)
if __name__=="__main__":main()
