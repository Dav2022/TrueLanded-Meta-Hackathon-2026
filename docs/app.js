"use strict";
(() => {
  const $ = id => document.getElementById(id);
  // Pinned to the three fictional source linesets, not a signature from Meta or any issuer.
  const EXPECTED_SOURCE_INDEX_SHA256 = "a0cc3282929ff0e67958ee27901016c7bcd21fd857d06796e3fa7d220e677ecc";
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
    // Bind all three independently checked source hashes to one committed index.
    // This is a local integrity commitment, NOT an issuer or provider signature.
    const index = doc.stages.map(s => s.event_id + "\n" + s.source_sha256 + "\n").join("");
    const indexHash = hex(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(index)));
    if (indexHash !== EXPECTED_SOURCE_INDEX_SHA256) throw Error("SOURCE_INDEX_SHA256_MISMATCH");
    doc.verified_source_index_sha256 = indexHash;
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
    $("trace-hash").textContent="VERIFIED FICTIONAL SOURCE INDEX SHA-256: "+payload.verified_source_index_sha256;
  }
  function renderWhatIf() {
    const result = $("hyp-result");
    result.replaceChildren();
    if (!payload || !globalThis.TrueLandedCounterfactual) {
      result.append(el("p", "Hypothetical calculation unavailable: source not verified."));
      return;
    }
    try {
      const output = globalThis.TrueLandedCounterfactual.calculate(
        payload, $("hyp-quantity").value, $("hyp-total").value.trim()
      );
      result.className = "hyp-result good";
      const intro = el("p", "RECALCULATED HYPOTHESIS · NOT A SOURCE DOCUMENT", "hyp-kicker");
      const math = el("p", output.quantity + " × $" + output.unit_price_usd +
        " = $" + output.computed_total_usd + " · proposed line total $" +
        output.proposed_total_usd);
      const advice = el("p", "Next proof: " +
        (friendly[output.next_best_proof] || output.next_best_proof));
      const open = el("p", "Open: " +
        output.open_obligations.map(x => friendly[x] || x).join(" · "));
      const changed = el("p", "New: " +
        (output.newly_exposed.map(x => friendly[x] || x).join(", ") || "none") +
        " · Conditionally reconciled: " +
        (output.conditionally_reconciled.map(x => friendly[x] || x).join(", ") || "none"));
      const scope = el("p", "Fictional browser calculation only · source unchanged · no Meta call · human review required.", "hyp-scope");
      result.append(intro, math, advice, open, changed, scope);
    } catch (error) {
      result.className = "hyp-result fail";
      result.append(el("p", "REFUSED: " +
        (error instanceof Error ? error.message : "INVALID_HYPOTHESIS")));
    }
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
      if (!globalThis.TrueLandedCounterfactual) throw Error("HYPOTHETICAL_ENGINE_MISSING");
      $("hyp-apply").addEventListener("click", renderWhatIf);
      $("hyp-reset").addEventListener("click", () => {
        $("hyp-quantity").value = "28";
        $("hyp-total").value = "235.06";
        renderWhatIf();
      });
      renderWhatIf();
    } catch(e) { block(e instanceof Error ? e.message : "UNKNOWN_SOURCE_ERROR"); }
  }
  load();
})();