"use strict";
(()=>{const $=id=>document.getElementById(id);let result=null;
function node(t,text,cls){const n=document.createElement(t);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;}
function row(a,b){const x=node('div',undefined,'field');x.append(node('b',a),node('span',b));return x;}
function show(n){if(!result)return;const cur=result.phases[n];$('tabs').replaceChildren();
result.phases.forEach((p,i)=>{const b=node('button',`${i+1}. ${p.event_id.replaceAll('_',' ')}`);b.disabled=i===n;b.addEventListener('click',()=>show(i));$('tabs').append(b);});
const el=$('scene');el.replaceChildren();el.append(node('h3','Evidence Spotlight'),row('Verified source literal count',cur.verified_literals),row('Source SHA-256',cur.source_sha256));
const list=node('ol');cur.fictional_source_lines.forEach(line=>list.append(node('li',line)));el.append(list);
el.append(node('h3','Next Best Proof'),row('Next required evidence',cur.next_best_proof),row('Still open',cur.open_obligations.join(', ')||'None'));
el.append(node('h3','Counterfactual Cascade'),row('Newly exposed',cur.newly_exposed.join(', ')||'None'),row('Conditionally reconciled',cur.conditionally_reconciled.join(', ')||'None'));
el.append(node('p','The source issuer is unverified. No binding customs determination; a human must review.','note'));
}
async function load(){try{const r=await fetch('/api/private-capture-scene',{cache:'no-store',credentials:'omit',mode:'same-origin',redirect:'error'});if(!r.ok)throw Error('SOURCE_GATE_HTTP_'+r.status);const o=await r.json();
if(o.gate!=='DF040_PRIVATE_OWNER_CAPTURE_DERIVED_REPLAY_PASS'||o.mode!=='OWNER_EXECUTED_META_CAPTURE_REPLAY_NOT_NEW_INFERENCE'||o.model_requested!=='muse-spark-1.3'||o.model_self_reported!=='muse-spark-1.3'||o.local_capture_http_status!==200||o.verified_literal_count!==18||o.provider_signed!==false||o.provider_origin_independently_attested!==false||o.model_calls_during_this_replay!==0||o.public_release_approved!==false||o.calculation_owner!=='TRUELANDED_DETERMINISTIC_CODE_NOT_META'||!Array.isArray(o.phases)||o.phases.length!==3)throw Error('PROVENANCE_CONTRACT_REJECTED');
for(const p of o.phases){if(p.source_document_authenticated!==false||p.human_review_required!==true||p.verified_literals!==p.fictional_source_lines.length)throw Error('SOURCE_NOT_VERIFIED');}
result=o;$('gate').textContent='OWNER-EXECUTED MUSE CAPTURE · 18/18 SOURCE LITERALS VERIFIED';$('hashes').textContent='Private response SHA-256: '+o.capture_sha256;show(0);
}catch(e){result=null;$('gate').textContent='DISPLAY REFUSED';$('hashes').textContent='Private source validation failed';$('tabs').replaceChildren();$('scene').replaceChildren(node('p',String(e.message)));}}
load();})();