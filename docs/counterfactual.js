/* DF-071: bounded, local, deterministic hypothetical calculations.
 * The source document is never changed; this module does not invoke Meta.
 * It is a browser-side example, not an issuer, tariff or legal authority.
 */
(function (root) {
  "use strict";
  function refuse(code) { throw new Error(code); }
  function literal(lines, key) {
    if (!Array.isArray(lines)) refuse("MISSING_FICTIONAL_SOURCE");
    const matches = lines.filter(line => typeof line === "string" && line.startsWith(key + ": "));
    if (matches.length !== 1) refuse("AMBIGUOUS_SOURCE_LITERAL");
    return matches[0].slice(key.length + 2);
  }
  function quantity(value) {
    if (typeof value !== "string" || !/^(?:[1-9]|[1-9][0-9]{1,2})$/.test(value))
      refuse("QUANTITY_MUST_BE_1_TO_999_WHOLE_PCS");
    return Number(value);
  }
  function moneyCents(value) {
    if (typeof value !== "string" || !/^(?:0|[1-9][0-9]{0,5})\.[0-9]{2}$/.test(value))
      refuse("USD_AMOUNT_MUST_HAVE_TWO_DECIMALS");
    const parts = value.split(".");
    const cents = Number(parts[0]) * 100 + Number(parts[1]);
    if (!Number.isSafeInteger(cents) || cents > 99999999)
      refuse("USD_AMOUNT_OUT_OF_RANGE");
    return cents;
  }
  function sourceQty(value) {
    const m = /^([1-9][0-9]{0,2}) PCS$/.exec(value);
    if (!m) refuse("FICTIONAL_SOURCE_QUANTITY_INVALID");
    return Number(m[1]);
  }
  function calculate(data, proposedQuantity, proposedTotal) {
    if (!data || !Array.isArray(data.stages) || data.stages.length !== 3 ||
        data.mode !== "SIMULATED_OFFLINE_NOT_META_INFERENCE")
      refuse("VERIFIED_SYNTHETIC_SCENE_REQUIRED");
    const packing = data.stages[0], invoice = data.stages[1];
    if (packing.event_id !== "PACKING_NEW" ||
        invoice.event_id !== "INVOICE_REVISED_INCONSISTENT")
      refuse("SOURCE_EVENT_ORDER_REFUSED");
    const packed = sourceQty(literal(packing.source_lines, "PACKED QUANTITY"));
    const baselineQty = sourceQty(literal(invoice.source_lines, "QUANTITY"));
    const unitCents = moneyCents(literal(invoice.source_lines, "UNIT PRICE").replace(/^USD /, ""));
    const baselineTotal = moneyCents(literal(invoice.source_lines, "LINE TOTAL").replace(/^USD /, ""));
    const qty = quantity(proposedQuantity);
    const totalCents = moneyCents(proposedTotal);
    if (unitCents <= 0 || packed !== 28 || baselineQty !== 28 ||
        baselineTotal !== 23506 || unitCents !== 792 ||
        JSON.stringify(invoice.open_obligations) !==
          JSON.stringify(["TECHNICAL_GAP", "VALUE_MISMATCH"]))
      refuse("EXPECTED_SYNTHETIC_SCENARIO_DRIFT");
    const open = [];
    if (qty !== packed) open.push("QTY_MISMATCH");
    open.push("TECHNICAL_GAP"); // Missing fictional specification is not provided by this scenario.
    if (qty * unitCents !== totalCents) open.push("VALUE_MISMATCH");
    const baseline = invoice.open_obligations;
    return Object.freeze({
      scenario_only: true,
      model_inference_performed: false,
      issuer_authenticated: false,
      human_review_required: true,
      original_sources_unchanged: true,
      quantity: qty,
      packed_quantity: packed,
      unit_price_usd: (unitCents / 100).toFixed(2),
      computed_total_usd: (qty * unitCents / 100).toFixed(2),
      proposed_total_usd: (totalCents / 100).toFixed(2),
      open_obligations: open,
      newly_exposed: open.filter(id => !baseline.includes(id)),
      conditionally_reconciled: baseline.filter(id => !open.includes(id)),
      next_best_proof: open.includes("QTY_MISMATCH") || open.includes("VALUE_MISMATCH")
        ? "REQ_RECONCILED_INVOICE" : "REQ_TECH_SHEET",
      ranking_semantics: "BOUNDED_ILLUSTRATIVE_CONDITIONAL_PRIORITY_NOT_REAL_WORLD_COST"
    });
  }
  root.TrueLandedCounterfactual = Object.freeze({ calculate });
})(globalThis);
