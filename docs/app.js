"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const STAGES = [
    ["PACKING_NEW", "Packing record", "Quantity mismatch"],
    ["INVOICE_REVISED_INCONSISTENT", "Invoice revision A", "Value mismatch"],
    ["INVOICE_REVISED_CORRECTED", "Invoice revision B", "Technical gap remains"]
  ];
  const EXPECTED_OPEN = [
    ["QTY_MISMATCH", "TECHNICAL_GAP"],
    ["TECHNICAL_GAP", "VALUE_MISMATCH"],
    ["TECHNICAL_GAP"]
  ];
  const EXPECTED_NEW = [[], ["VALUE_MISMATCH"], []];
  const EXPECTED_RECONCILED = [[], ["QTY_MISMATCH"], ["VALUE_MISMATCH"]];
  const EXPECTED_PROOF = ["REQ_RECONCILED_INVOICE", "REQ_RECONCILED_INVOICE", "REQ_TECH_SHEET"];
  const EXPECTED_COUNTS = [4, 7, 7];
  const friendly = {
    REQ_RECONCILED_INVOICE: "Request a reconciled invoice",
    REQ_TECH_SHEET: "Request the technical specification sheet",
    QTY_MISMATCH: "Quantity inconsistency",
    TECHNICAL_GAP: "Technical evidence missing",
    VALUE_MISMATCH: "Invoice value inconsistency"
  };
  let payload = null;
  function el(tag, text, cls) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = String(text);
    if (cls) node.className = cls;
    return node;
  }
  function same(a,b) { return Array.isArray(a) && JSON.stringify(a) === JSON.stringify(b); }
  function hex(bytes) { return [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,"0")).join(""); }
  async function sourceSha(lines) {
    const raw = new TextEncoder().encode(lines.join("\n")+"\n");
    return hex(await crypto.subtle.digest("SHA-256", raw));
  }
  async function validate(doc) {
    if (!doc || doc.schema !== "TRUELANDED_DF043_SYNTHETIC_STATIC_V1"
      || doc.mode !== "SIMULATED_OFFLINE_NOT_META_INFERENCE"
      || doc.model_candidate_source !== "LOCAL_TEST_DOUBLE_NOT_META"
      || doc.model_name_requested !== "muse-spark-1.3"
      || doc.meta_api_calls_during_site !== 0
      || doc.provider_signature_verified !== false
      || doc.private_receipt_included !== false
      || doc.source_document_issuers_authenticated !== false
      || doc.human_review_required !== true
      || doc.total_literal_matches !== 18
      || doc.final_next_best_proof !== "REQ_TECH_SHEET"
      || !Array.isArray(doc.stages) || doc.stages.length !== 3
      || !/^[0-9a-f]{64}$/.test(doc.source_pack_sha256)) throw Error("ATTRIBUTION_OR_SCOPE_CHECK_REFUSED");
    for (let i=0; i<3; i++) {
      const s=doc.stages[i];
      if (!s || s.event_id!==STAGES[i][0] || s.literal_matches!==EXPECTED_COUNTS[i]
        || !Array.isArray(s.source_lines) || s.source_lines.length!==EXPECTED_COUNTS[i]
        || s.human_review_required!==true || s.issuer_authenticated!==false
        || s.next_best_proof!==EXPECTED_PROOF[i]
        || !same(s.open_obligations,EXPECTED_OPEN[i])
        || !same(s.newly_exposed,EXPECTED_NEW[i])
        || !same(s.conditionally_reconciled,EXPECTED_RECONCILED[i])
        || !/^[a-f0-9]{64}$/.test(s.source_sha256)) throw Error("DETERMINISTIC_STAGE_CONTRACT_REFUSED");
      if (s.source_lines.some(line=>typeof line!=="string" || line.length>160 || line.includes("\r")))
        throw Error("UNSAFE_OR_MISSING_LITERAL");
      if (await sourceSha(s.source_lines)!==s.source_sha256) throw Error("SOURCE_SHA256_MISMATCH");
    }
    return doc;
  }
  function renderPills(targetId,values,cls) {
    const parent=$(targetId);
    parent.replaceChildren();
    if (!values.length) { parent.append(el("span","None","pill none"));return; }
    for (const code of values) parent.append(el("span",friendly[code]||code,"pill "+(cls||"")));
  }
  function renderStage(index) {
    const s=payload.stages[index];
    $("stage-trail").replaceChildren();
    STAGES.forEach((st,i)=>{
      const b=el("button",undefined,"stage-button");
      b.type="button"; b.setAttribute("aria-pressed",String(i===index));
      b.append(el("span","PHASE 0"+(i+1),"num"),el("strong",st[1]),el("span",st[2],"hint"));
      b.addEventListener("click",()=>renderStage(i));$("stage-trail").append(b);
    });
    $("doc-label").textContent=STAGES[index][1].toUpperCase();
    const lines=$("source-lines");lines.replaceChildren();
    for (const line of s.source_lines) lines.append(el("li",line));
    $("source-sha").textContent=s.source_sha256;
    $("literal-match").textContent=s.literal_matches+" / "+EXPECTED_COUNTS[index];
    $("next-proof").textContent=friendly[s.next_best_proof]||s.next_best_proof;
    renderPills("open-obligations",s.open_obligations,"negative");
    renderPills("newly-exposed",s.newly_exposed,"negative");
    renderPills("reconciled",s.conditionally_reconciled,"positive");
    $("trace-hash").textContent="SOURCE PACK SHA-256: "+payload.source_pack_sha256;
  }
  function block(reason) {
    payload=null;
    $("validation").className="validation fail";
    $("validation").textContent="VERIFICATION FAILED · DO NOT RELY ON DISPLAY";
    $("stage-trail").replaceChildren(el("span","EVIDENCE REFUSED"));
    $("source-lines").replaceChildren();
    $("source-sha").textContent="NOT VERIFIED";
    $("literal-match").textContent="0 / 18";
    $("next-proof").textContent="NO RECOMMENDATION";
    renderPills("open-obligations",[],"");
    renderPills("newly-exposed",[],"");
    renderPills("reconciled",[],"");
    $("trace-hash").textContent=String(reason).slice(0,80);
  }
  async function load() {
    try {
      if (!globalThis.crypto || !globalThis.crypto.subtle) throw Error("SECURE_CONTEXT_REQUIRED");
      const r=await fetch("data.json",{credentials:"omit",cache:"no-store",redirect:"error"});
      if (!r.ok) throw Error("DATA_FETCH_"+r.status);
      const type=r.headers.get("content-type")||"";
      if (type.includes("text/html")) throw Error("EXPECTED_JSON_NOT_HTML");
      const body=await r.text();
      if (body.length>14000) throw Error("DATA_TOO_LARGE");
      payload=await validate(JSON.parse(body));
      $("validation").className="validation good";
      $("validation").textContent="18/18 SYNTHETIC SOURCE LITERALS VERIFIED";
      renderStage(0);
    } catch(e) { block(e instanceof Error ? e.message : "UNKNOWN_SOURCE_ERROR"); }
  }
  load();
})();