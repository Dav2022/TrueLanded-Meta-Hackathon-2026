"""DF-023L: single HTTPS exchange, called ONLY by owner-approved CLI.
No retries, no redirects, no automatic invocation or persistent credentials.
Returned bytes are UNTRUSTED until locally captured and verified.
"""
from __future__ import annotations
from urllib.request import Request,HTTPSHandler,ProxyHandler,HTTPRedirectHandler,build_opener
from urllib.error import HTTPError
import ssl
import df023j_plus_novel_muse as novel

ENDPOINT="https://api.meta.ai/v1/chat/completions"
MAX_BODY=160000
class TransportRefusal(ValueError):pass

class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):
  raise TransportRefusal("PROVIDER_REDIRECT_DENIED")

def exchange(request,token):
 """Exactly one network exchange; never read or log a secret."""
 if not isinstance(token,str) or not token.startswith("LLM") or len(token)<24:
  raise TransportRefusal("LOCAL_TOKEN_FORMAT_REFUSED")
 if request.get("model")!="muse-spark-1.3":
  raise TransportRefusal("MODEL_NOT_ALLOWLISTED")
 raw=novel.encoded(request)
 if len(raw)>17000:
  raise TransportRefusal("REQUEST_TOO_LARGE")
 opener=build_opener(ProxyHandler({}),NoRedirect(),
   HTTPSHandler(context=ssl.create_default_context()))
 r=Request(ENDPOINT,data=raw,method="POST",headers={
   "Authorization":"Bearer "+token,"Content-Type":"application/json",
   "Accept":"application/json","User-Agent":"TrueLanded-DF023L/1"})
 try:
  with opener.open(r,timeout=75) as http:
   return http.status,http.read(MAX_BODY+1)
 except HTTPError as ex:
  with ex:
   return ex.code,ex.read(MAX_BODY+1)
