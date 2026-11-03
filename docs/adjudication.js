"use strict";
(async () => {
  const $ = id => document.getElementById(id);
  const label = value => String(value).replaceAll("_", " ");
  // Independent release commitments, reviewed against 15fa673; never read from the response.
  // Pin the complete UTF-8 file, including its final LF, before parsing or rendering.
  const EXPECTED_DATA_SHA256 = "9fe6e2cd2fd640d28baaef5a68ad7af1c6c34e2d90a62b48db8a5b6364c612ea";
  const EXPECTED_ENGINE_SHA256 = "6dc5e8f2031999d9d9aa715450050156ae05c77ce185bd0d85784d180fb48ca3";
  const EXPECTED_FIXTURE_SHA256 = "0ed0a1555400cbcb55cb71572156578b66b3d89cf52435c9b0e733cda4e1d814";
  const EXPECTED_CASE_IDS = [
    "T01_BASE_DOCUMENTED_THREE", "T02_ZERO_DIFFERENCE", "T03_SURPLUS_ACTA",
    "T04_INVOICE_68_PIECES", "T05_INVOICE_65_PIECES", "T06_INVOICE_WEIGHT_3_KG",
    "T07_MISSING_ACTA_OBSERVATION", "T08_MISSING_BL_OBSERVATION", "T09_UNVERIFIED_BL_OCR_ONLY",
    "T10_UNVERIFIED_ACTA_OCR_ONLY", "T11_TWO_ACTA_SAME_VALUE", "T12_ACTA_65_VS_52",
    "T13_BL_68_VS_70", "T14_SHIPMENT_CONTEXT_MISMATCH", "T15_OBSERVATION_SOURCE_HASH_SWAPPED",
    "T16_DUPLICATE_BINARY_AS_DIFFERENT_DOC", "T17_INVOICE_PIECES_AS_PACKAGES", "T18_INVOICE_IMPERSONATES_BL",
    "T19_BOOL_QUANTITY_NOT_INTEGER", "T20_FORGED_PRIVACY_APPROVAL", "T21_FAKE_HUMAN_SOURCE_APPROVAL",
    "T22_DUPLICATE_OBSERVATION_ID", "T23_ORPHAN_OBSERVATION", "T24_UNKNOWN_FIELD",
    "T25_BAD_ORIGINAL_HASH", "T26_PAGE_OUTSIDE_DOCUMENT", "T27_PROHIBITED_HTML_SOURCE_CLAIM",
    "T28_UNKNOWN_PRIVACY_KEY", "T29_DIFFERENT_UNIT_WEIGHT_WRONG_ROLE", "T30_FINAL_REVIEW_FLAG_FORGERY"
  ];
  const STATUSES = new Set([
    "DOCUMENTARY_QUANTITY_DIFFERENCE_FOR_REVIEW", "NO_DOCUMENTARY_PACKAGE_DIFFERENCE_FOR_REVIEW",
    "DOCUMENTARY_QUANTITY_SURPLUS_FOR_REVIEW", "BLOCKED_INSUFFICIENT_VISUALLY_CORRELATED_SOURCES",
    "BLOCKED_CONFLICTING_PRIMARY_DOCUMENT_EVIDENCE", "REJECTED_INPUT"
  ]);
  let verified = false;
  function clearResults() {
    verified = false;
    $("lab-case").disabled = true;
    $("lab-case").replaceChildren();
    $("lab-inputs").replaceChildren();
    $("lab-status").textContent = "NO RECOMMENDATION";
    for (const id of ["lab-delta", "lab-excluded", "lab-lineage"]) $(id).textContent = "";
    $("lab-integrity").textContent = "INTEGRITY NOT VERIFIED";
  }
  function refuse() {
    clearResults();
    $("lab-validation").className = "validation fail";
    $("lab-validation").textContent = "REPLAY REFUSED";
  }
  function requireThat(condition) {
    if (!condition) throw Error("REPLAY_CONTRACT_REFUSED");
  }
  function exactKeys(value, keys) {
    requireThat(value !== null && typeof value === "object" && !Array.isArray(value));
    requireThat(Object.keys(value).length === keys.length
      && keys.every(key => Object.prototype.hasOwnProperty.call(value, key)));
  }
  const count = value => Number.isSafeInteger(value) && value >= 0;
  const optionalCount = value => value === null || count(value);
  function validate(data) {
    exactKeys(data, ["schema", "mode", "engine_sha256", "fixture_sha256", "human_review_required",
      "issuer_authenticated", "legal_action_authorized", "meta_calls", "cases"]);
    requireThat(data.schema === "DF073_SYNTHETIC_PRECOMPUTED_ADJUDICATION_V1"
      && data.mode === "PRECOMPUTED_PYTHON_RESULTS_NOT_LIVE_INFERENCE"
      && data.engine_sha256 === EXPECTED_ENGINE_SHA256 && data.fixture_sha256 === EXPECTED_FIXTURE_SHA256
      && data.meta_calls === 0 && data.human_review_required === true
      && data.legal_action_authorized === false && data.issuer_authenticated === false
      && Array.isArray(data.cases) && data.cases.length === EXPECTED_CASE_IDS.length);
    const ids = new Set();
    data.cases.forEach((c, index) => {
      exactKeys(c, ["id", "inputs", "output", "matches_expected"]);
      requireThat(c.id === EXPECTED_CASE_IDS[index] && !ids.has(c.id) && c.matches_expected === true);
      ids.add(c.id);
      requireThat(Array.isArray(c.inputs) && c.inputs.length > 0 && c.inputs.length <= 100);
      c.inputs.forEach(o => {
        exactKeys(o, ["role", "field", "unit", "value"]);
        for (const key of ["role", "field", "unit"])
          requireThat(typeof o[key] === "string" && /^[a-z_]{1,64}$/.test(o[key]));
        // These are attack inputs, not accepted engine evidence: T19 intentionally contains a boolean.
        requireThat(typeof o.value === "boolean" || count(o.value));
      });
      const r = c.output;
      exactKeys(r, ["status", "declared", "inspected", "difference", "excluded", "evidence_nodes"]);
      requireThat(STATUSES.has(r.status) && optionalCount(r.declared) && optionalCount(r.inspected)
        && (r.difference === null || Number.isSafeInteger(r.difference))
        && optionalCount(r.excluded) && count(r.evidence_nodes));
      if (r.status === "REJECTED_INPUT") {
        requireThat(r.declared === null && r.inspected === null && r.difference === null
          && r.excluded === null && r.evidence_nodes === 0);
      } else {
        requireThat(count(r.excluded) && r.evidence_nodes > 0);
        if (r.status.startsWith("BLOCKED_")) {
          requireThat(r.difference === null && (r.declared === null || r.inspected === null));
        } else {
          requireThat(count(r.declared) && count(r.inspected)
            && r.difference === r.declared - r.inspected);
          const expected = r.difference > 0 ? "DOCUMENTARY_QUANTITY_DIFFERENCE_FOR_REVIEW"
            : r.difference < 0 ? "DOCUMENTARY_QUANTITY_SURPLUS_FOR_REVIEW"
            : "NO_DOCUMENTARY_PACKAGE_DIFFERENCE_FOR_REVIEW";
          requireThat(r.status === expected);
        }
      }
    });
    return data;
  }
  clearResults();
  $("lab-validation").className = "validation";
  $("lab-validation").textContent = "VERIFYING REPLAY INTEGRITY";
  try {
    if (!globalThis.crypto || !globalThis.crypto.subtle) throw Error("SECURE_CONTEXT_REQUIRED");
    const response = await fetch("adjudication-data.json", {credentials:"omit",cache:"no-store",redirect:"error"});
    if (!response.ok) throw Error("DATA_UNAVAILABLE");
    const type = response.headers.get("content-type") || "";
    if (!/^application\/json(?:\s*;|\s*$)/i.test(type)) throw Error("EXPECTED_JSON");
    const raw = new Uint8Array(await response.arrayBuffer());
    if (raw.byteLength > 80000) throw Error("DATA_TOO_LARGE");
    const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", raw));
    const hash = [...digest].map(x => x.toString(16).padStart(2, "0")).join("");
    if (hash !== EXPECTED_DATA_SHA256) throw Error("DATA_SHA256_MISMATCH");
    const data = validate(JSON.parse(new TextDecoder("utf-8", {fatal:true}).decode(raw)));
    const picker = $("lab-case");
    data.cases.forEach(c => { const option=document.createElement("option"); option.value=c.id; option.textContent=label(c.id); picker.append(option); });
    function render() {
      if (!verified) throw Error("REPLAY_NOT_VERIFIED");
      const current=data.cases.find(c=>c.id===picker.value);
      if (!current) throw Error("UNKNOWN_CASE");
      const r=current.output;
      $("lab-inputs").replaceChildren(...current.inputs.map(o=>{
        const li=document.createElement("li");
        li.textContent=label(o.role)+" · "+label(o.field)+": "+String(o.value)+" "+label(o.unit);
        return li;
      }));
      $("lab-status").textContent=label(r.status);
      $("lab-delta").textContent=r.difference===null ? "No documentary arithmetic permitted." : "Declared: "+r.declared+" packages · Inspected: "+r.inspected+" packages · Difference: "+r.difference+" packages for review.";
      $("lab-excluded").textContent="Noncomparable observations excluded: "+(r.excluded===null?"input rejected":r.excluded);
      $("lab-lineage").textContent="Traceable evidence nodes: "+r.evidence_nodes+" · No legal action authorized.";
    }
    picker.addEventListener("change", () => { try { render(); } catch { refuse(); } });
    verified = true;
    render();
    picker.disabled = false;
    $("lab-validation").className="validation good";
    $("lab-validation").textContent="30 / 30 SYNTHETIC EXPECTED VERDICTS · PRECOMPUTED REPLAY";
    $("lab-integrity").textContent="Verified replay SHA-256: "+hash+". Engine SHA-256: "+EXPECTED_ENGINE_SHA256+". Local release integrity reference; not a Meta or issuer signature.";
  } catch (error) {
    refuse();
  }
})();
