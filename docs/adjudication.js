"use strict";
(async () => {
  const $ = id => document.getElementById(id);
  const label = value => String(value).replaceAll("_", " ");
  try {
    const response = await fetch("adjudication-data.json", {credentials:"omit",cache:"no-store",redirect:"error"});
    if (!response.ok) throw Error("DATA_UNAVAILABLE");
    const raw = await response.text();
    if (raw.length > 80000) throw Error("DATA_TOO_LARGE");
    const data = JSON.parse(raw);
    if (data.schema !== "DF073_SYNTHETIC_PRECOMPUTED_ADJUDICATION_V1" || data.meta_calls !== 0 || data.human_review_required !== true || data.legal_action_authorized !== false || data.issuer_authenticated !== false || !Array.isArray(data.cases) || data.cases.length !== 30 || data.cases.some(c => c.matches_expected !== true)) throw Error("SCOPE_REFUSED");
    const picker = $("lab-case");
    data.cases.forEach(c => { const option=document.createElement("option"); option.value=c.id; option.textContent=label(c.id); picker.append(option); });
    function render() {
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
    picker.addEventListener("change",render); render();
    $("lab-validation").className="validation good";
    $("lab-validation").textContent="30 / 30 SYNTHETIC EXPECTED VERDICTS · PRECOMPUTED REPLAY";
    $("lab-integrity").textContent="Engine SHA-256: "+data.engine_sha256+". Self-issued integrity reference; not a Meta or issuer signature.";
  } catch (error) {
    $("lab-validation").className="validation fail";
    $("lab-validation").textContent="REPLAY REFUSED";
    $("lab-case").disabled=true;
    $("lab-inputs").replaceChildren();
    $("lab-status").textContent="NO RECOMMENDATION";
  }
})();
