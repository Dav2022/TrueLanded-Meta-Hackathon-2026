"""DF040 immutable private owner-capture review; localhost-only, no Meta API."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'integration'))
import df040_capture_projection as projection
HEADERS={'Cache-Control':'no-store','X-Frame-Options':'DENY',
'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
'Cross-Origin-Resource-Policy':'same-origin',
'Content-Security-Policy':"default-src 'none';script-src 'self';style-src 'self';connect-src 'self';img-src 'self' data:;base-uri 'none';form-action 'none';frame-ancestors 'none"}
FILES={'/':'index.html','/index.html':'index.html','/ui.js':'ui.js','/style.css':'style.css'}
class Handler(BaseHTTPRequestHandler):
 server_version='TrueLanded-DF040-PrivateVerifiedReplay';sys_version=''
 def log_message(self,*args):pass
 def reply(self,code,obj,mime='application/json; charset=utf-8'):
  body=obj if isinstance(obj,bytes) else json.dumps(obj,ensure_ascii=True).encode('utf8')
  if len(body)>60000:code,body=503,b'{"error":"SIZE_REFUSAL"}'
  self.send_response(code);self.send_header('Content-Type',mime)
  self.send_header('Content-Length',str(len(body)))
  for k,v in HEADERS.items():self.send_header(k,v)
  self.end_headers()
  try:self.wfile.write(body)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_GET(self):
  hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
  if (self.headers.get('Host','') not in hosts or
      self.headers.get('Origin','') not in ('',*[f'http://{x}' for x in hosts]) or
      self.headers.get('Cookie') or self.headers.get('Authorization') or
      self.headers.get('Sec-Fetch-Site')=='cross-site'):
   return self.reply(403,{'error':'SAME_ORIGIN_LOCAL_ONLY'})
  path=urlsplit(self.path)
  if path.query or path.fragment:return self.reply(422,{'error':'NO_QUERIES'})
  if path.path=='/api/private-capture-scene':
   try:return self.reply(200,projection.project(self.server.private_evidence_dir))
   except Exception:return self.reply(503,{'error':'PRIVATE_CAPTURE_VERIFICATION_FAILED'})
  if path.path in FILES:
   name=FILES[path.path];f=ROOT/name
   if not f.is_file() or f.is_symlink():return self.reply(503,{'error':'ASSET_MISSING'})
   mime='text/html; charset=utf-8' if name.endswith('.html') else ('text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8')
   return self.reply(200,f.read_bytes(),mime)
  return self.reply(404,{'error':'ROUTE_NOT_ALLOWED'})
 def do_POST(self):self.reply(405,{'error':'READ_ONLY'})
 def do_PUT(self):self.do_POST()
 def do_PATCH(self):self.do_POST()
 def do_DELETE(self):self.do_POST()
 def do_OPTIONS(self):self.do_POST()
def main():
 cli=argparse.ArgumentParser();cli.add_argument('--private-evidence-dir',required=True)
 cli.add_argument('--port',type=int,default=18972)
 a=cli.parse_args()
 if not 1024<=a.port<=65535:raise SystemExit('INVALID_PORT')
 projection.project(a.private_evidence_dir)
 with ThreadingHTTPServer(('127.0.0.1',a.port),Handler) as server:
  server.private_evidence_dir=a.private_evidence_dir
  print(f'DF040_PRIVATE_OWNER_CAPTURE_REPLAY=http://127.0.0.1:{a.port}/',flush=True)
  server.serve_forever(poll_interval=.2)
if __name__=='__main__':main()