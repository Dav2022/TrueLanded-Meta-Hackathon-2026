"""DF037 standalone localhost-only read-only simulated evidence demo."""
from __future__ import annotations
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
import json,sys,argparse
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'integration'))
import df037_mock_pipeline

HEADERS={'Cache-Control':'no-store','X-Frame-Options':'DENY',
'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
'Cross-Origin-Resource-Policy':'same-origin',
'Content-Security-Policy':"default-src 'none';script-src 'self';style-src 'self';connect-src 'self';img-src 'self' data:;base-uri 'none';form-action 'none';frame-ancestors 'none"}
ASSETS={'/':'index.html','/index.html':'index.html','/ui.js':'ui.js','/style.css':'style.css'}
class Handler(BaseHTTPRequestHandler):
    server_version='TrueLanded-DF037-Simulated-Demo';sys_version=''
    def log_message(self,*args):pass
    def send(self,code,body,mime='application/json; charset=utf-8'):
        if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=True).encode('utf8')
        if len(body)>100000:code,body=503,b'{"error":"SIZE_GATE"}'
        self.send_response(code);self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(body)))
        for k,v in HEADERS.items():self.send_header(k,v)
        self.end_headers()
        try:self.wfile.write(body)
        except (ConnectionResetError,BrokenPipeError):pass
    def do_GET(self):
        hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        if (self.headers.get('Host','') not in hosts or
            self.headers.get('Origin','') not in ('',*[f'http://{host}' for host in hosts]) or
            self.headers.get('Cookie') or self.headers.get('Authorization') or
            self.headers.get('Sec-Fetch-Site')=='cross-site'):
            return self.send(403,{'error':'LOCAL_ONLY'})
        path=urlsplit(self.path)
        if path.query or path.fragment:return self.send(422,{'error':'NO_QUERY'})
        if path.path=='/api/mock-scene':
            try:
                outcome=df037_mock_pipeline.execute()
                if outcome['gate']!='DF037_FULL_PIPELINE_MOCK_SOURCE_CHECKED':
                    return self.send(503,{'error':'SOURCE_VALIDATION_DENIED'})
                return self.send(200,outcome)
            except Exception:return self.send(503,{'error':'SOURCE_VALIDATION_DENIED'})
        if path.path in ASSETS:
            name=ASSETS[path.path];file=ROOT/name
            if file.is_symlink() or not file.is_file():return self.send(503,{'error':'ASSET_MISSING'})
            mime='text/html; charset=utf-8' if name.endswith('.html') else ('text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8')
            return self.send(200,file.read_bytes(),mime)
        return self.send(404,{'error':'NOT_FOUND'})
    def do_POST(self):self.send(405,{'error':'READ_ONLY'})
    def do_PUT(self):self.do_POST()
    def do_PATCH(self):self.do_POST()
    def do_DELETE(self):self.do_POST()
    def do_OPTIONS(self):self.do_POST()
def main():
    arg=argparse.ArgumentParser();arg.add_argument('--port',type=int,default=18971)
    opts=arg.parse_args()
    if not 1024<=opts.port<=65535:raise SystemExit('INVALID_PORT')
    with ThreadingHTTPServer(('127.0.0.1',opts.port),Handler) as server:
        print(f'DF037_SIMULATION_ONLY=http://127.0.0.1:{opts.port}/',flush=True)
        server.serve_forever(poll_interval=.2)
if __name__=='__main__':main()