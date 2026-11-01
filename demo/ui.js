"use strict";
(()=>{const $=id=>document.getElementById(id);let payload=null;
function elt(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;}
function field(label,value){const row=elt('div',undefined,'field');row.append(elt('b',label),elt('span',value));return row;}
function show(n){if(!payload)return;const stage=payload.stages[n];$('tabs').replaceChildren();
 payload.stages.forEach((s,i)=>{const b=elt('button',`${i+1}. ${s.stage.replaceAll('_',' ')}`);b.disabled=(i===n);b.addEventListener('click',()=>show(i));$('tabs').append(b);});
 const scene=$('scene');scene.replaceChildren();
 scene.append(elt('h3','Evidence Spotlight'),field('Fictional source SHA-256',stage.source_sha256),field('Exact source literals',stage.literal_matches));
 const lines=elt('ol');for(const item of stage.source_lines){lines.append(elt('li',item));}scene.append(lines);
 scene.append(elt('h3','Next Best Proof'),field('Highest priority document',stage.next_best_proof),field('Open obligations',stage.open_obligations.join(', ')||'none'));
 scene.append(elt('h3','Counterfactual Cascade'),field('Newly exposed',stage.newly_exposed.join(', ')||'none'),field('Conditionally reconciled',stage.conditionally_reconciled.join(', ')||'none'));
 scene.append(elt('p','Hypothetical documents · issuer not authenticated · human review required.','note'));
}
async function load(){try{const response=await fetch('/api/mock-scene',{cache:'no-store',credentials:'omit',redirect:'error',mode:'same-origin'});if(!response.ok)throw Error('SOURCE_GATE_HTTP_'+response.status);const o=await response.json();
if(o.gate!=='DF037_FULL_PIPELINE_MOCK_SOURCE_CHECKED'||o.mode!=='SIMULATED_OFFLINE_NOT_META_INFERENCE'||o.meta_inference_proven!==false||o.api_calls!==0||o.literal_matches!==18||o.calculation_owner!=='TRUELANDED_DETERMINISTIC_CODE_NOT_META'||o.provider_signed!==false||o.human_review_required!==true||!Array.isArray(o.stages)||o.stages.length!==3)throw Error('PROVENANCE_GATE_REFUSED');
for(const row of o.stages){if(row.source_document_authenticated!==false||row.human_review_required!==true||row.literal_matches!==row.source_lines.length)throw Error('SOURCE_GATE_REFUSED');}
payload=o;$('gate').textContent='18 / 18 SIMULATED SOURCE LITERALS VERIFIED · NOT META INFERENCE';$('hashes').textContent='Request SHA-256: '+o.request_sha256;show(0);
}catch(error){payload=null;$('gate').textContent='DISPLAY BLOCKED';$('hashes').textContent='Evidence validation failed';$('scene').replaceChildren(elt('p',String(error.message)));$('tabs').replaceChildren();}}
load();})();