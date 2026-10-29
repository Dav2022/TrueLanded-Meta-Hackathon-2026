"use strict";
/* DF-023M private jury replay: no model calls and no provider receipt in client.
 * The server MUST verify its entire exported manifest before each response.
 * Never render stale data after a verification request fails.
 */
(()=>{const $=id=>document.getElementById(id),buttons=[...document.querySelectorAll("[data-stage]")];
let stages=null,selected=0,verified=false,blockedByDemo=false;
const human=x=>String(x||"NONE").replaceAll("_"," ");
function blanks(){
 for(const [id,value] of Object.entries({
  stageFields:"—",stageOpenCount:"—",nextProof:"BLOCKED",
  stageTitle:"EVIDENCE NOT VERIFIED",stageDescription:"Local integrity gate unavailable",
  fieldCount:"NOT VERIFIED",sourceHash:"—",responseHash:"—"}))$(id).textContent=value;
 for(const id of ["openList","newList","closedList","sourceTable"])$(id).replaceChildren();
 for(const id of ["checkSource","checkDiff","checkHuman"])$(id).textContent="○";
}
function lock(reason){
 verified=false;stages=null;blanks();
 $("gateBanner").className="gate bad";$("gateLabel").textContent="DISPLAY BLOCKED";
 $("gateSecondary").textContent=String(reason).slice(0,95);
}
function list(id,arr){
 const target=$(id);target.replaceChildren();
 if(!arr.length){const li=document.createElement("li");li.textContent="None in this fictional stage";target.append(li);}
 for(const item of arr){const li=document.createElement("li");li.textContent=human(item);target.append(li);}
}
function paint(n){
 if(!verified||!stages||n<0||n>=stages.length)return lock("MANDATORY_GATE_NOT_AVAILABLE");
 selected=n;
 const t=stages[n];
 if(t.human_review_required!==true||t.source_document_authenticated!==false||
   t.ranked_proof_request_is_executed!==false||t.verified_literal_line_count!==t.fictional_source_lines.length)
  return lock("SOURCE_OR_AUTHORITY_GATE_REFUSED");
 const names=[
  "Packing reconfirmation",
  "First fictional invoice revision",
  "Second fictional invoice revision"];
 const descriptions=[
  "The fictional packing statement keeps the quantity discrepancy open. A technical specification is still missing.",
  "The quantity now agrees conditionally, but the revised invoice exposes a new arithmetic value conflict.",
  "The amount reconciles conditionally. The missing technical sheet remains the next evidence to seek."];
 $("stageTitle").textContent=names[n];$("stageDescription").textContent=descriptions[n];
 $("stageFields").textContent=t.verified_literal_line_count+" / "+t.fictional_source_lines.length;
 $("stageOpenCount").textContent=t.open_obligations.length+" obligations";
 $("nextProof").textContent=human(t.top_next_proof_request);
 list("openList",t.open_obligations);list("newList",t.newly_exposed);
 list("closedList",t.conditionally_reconciled);
 const container=$("sourceTable");container.replaceChildren();
 for(let i=0;i<t.fictional_source_lines.length;i++){
  const node=document.createElement("div");node.className="line";
  const number=document.createElement("b");number.textContent=String(i+1).padStart(2,"0");
  const value=document.createElement("span");value.textContent=t.fictional_source_lines[i];
  node.append(number,value);container.append(node);
 }
 $("sourceHash").textContent=t.source_sha256;
 buttons.forEach(button=>button.classList.toggle("selected",Number(button.dataset.stage)===n));
}
async function load(){
 if(blockedByDemo)return;
 blanks();
 $("gateBanner").className="gate pending";
 $("gateLabel").textContent="CHECKING EXPORTED SOURCE INTEGRITY";
 $("gateSecondary").textContent="No display before local manifest verification";
 try{
  const answer=await fetch("/api/scene",{cache:"no-store",credentials:"omit",
                            redirect:"error",mode:"same-origin"});
  if(!answer.ok)throw Error("MANDATORY_LOCAL_GATE_HTTP_"+answer.status);
  const d=await answer.json(),m=d.manifest,e=d.evidence;
  if(!d||d.gate!=="DF023M_SELF_CHECKED_LOCAL_REPLAY"||
     !m||m.public_release_approved!==false||m.redistribution_license_granted!==false||
     !e||e.schema!=="DF023M_JURY_DERIVED_REPLAY_V1"||
     e.gate!=="OWNER_LOCAL_DERIVED_META_RESULT_SOURCE_VERIFIED"||
     e.model_reported!=="muse-spark-1.3"||
     e.literal_candidates_verified_against_fictional_source!==18||
     e.public_release_approved!==false||e.issuer_authenticated!==false||
     e.human_review_required!==true||e.provider_signed!==false||
     e.actual_provider_response_body_embedded!==false||
     e.meta_api_calls_from_this_package!==0||
     e.final_next_proof!=="REQ_TECH_SHEET"||
     !Array.isArray(e.source_documents)||e.source_documents.length!==3||
     e.source_documents.reduce((x,t)=>x+t.fictional_source_lines.length,0)!==18)
   throw Error("JURY_SOURCE_OR_AUTHORITY_CONTRACT_REFUSED");
  stages=e.source_documents;verified=true;
  $("fieldCount").textContent="18 / 18";
  $("responseHash").textContent=e.original_provider_response_local_sha256;
  $("gateBanner").className="gate good";
  $("gateLabel").textContent="REAL MUSE RESULT · OWNER-VERIFIED DERIVED REPLAY";
  $("gateSecondary").textContent="18 literal matches · source hash gate passed · not provider-signed";
  for(const id of ["checkSource","checkDiff","checkHuman"])$(id).textContent="✓";
  paint(selected);
 }catch(error){lock(error.message);}
}
for(const button of buttons)button.addEventListener("click",()=>paint(Number(button.dataset.stage)));
$("simulateFail").addEventListener("click",()=>{
 if(!blockedByDemo){
  blockedByDemo=true;
  lock("SIMULATED_VERIFICATION_FAILURE: all staged claims cleared");
  $("simulateFail").textContent="Restore independently checked replay";
 }else{
  blockedByDemo=false;$("simulateFail").textContent="Simulate a missing verification";
  load();
 }
});
load();
})();
