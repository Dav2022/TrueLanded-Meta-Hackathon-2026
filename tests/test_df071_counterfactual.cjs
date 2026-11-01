/* DF-071 adversarial what-if test suite: no external dependencies or API calls. */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const scene = JSON.parse(fs.readFileSync(path.join(root, "docs", "data.json"), "utf8"));
const source = fs.readFileSync(path.join(root, "docs", "counterfactual.js"), "utf8");
const sandbox = {};
vm.runInNewContext(source, sandbox, { timeout: 800 });
const calc = sandbox.TrueLandedCounterfactual.calculate;
const plain = o => JSON.parse(JSON.stringify(o));

test("baseline calculation matches published fictional invoice A", () => {
  const x = plain(calc(scene, "28", "235.06"));
  assert.equal(x.computed_total_usd, "221.76");
  assert.equal(x.next_best_proof, "REQ_RECONCILED_INVOICE");
  assert.deepEqual(x.open_obligations, ["TECHNICAL_GAP", "VALUE_MISMATCH"]);
  assert.equal(x.model_inference_performed, false);
  assert.equal(x.original_sources_unchanged, true);
  assert.equal(x.human_review_required, true);
});
test("correcting fictional amount reveals technical proof as next priority", () => {
  const x = plain(calc(scene, "28", "221.76"));
  assert.deepEqual(x.open_obligations, ["TECHNICAL_GAP"]);
  assert.deepEqual(x.conditionally_reconciled, ["VALUE_MISMATCH"]);
  assert.equal(x.next_best_proof, "REQ_TECH_SHEET");
});
test("new quantity discrepancy is computed, not selected from static JSON", () => {
  const x = plain(calc(scene, "31", "245.52"));
  assert.deepEqual(x.open_obligations, ["QTY_MISMATCH", "TECHNICAL_GAP"]);
  assert.deepEqual(x.newly_exposed, ["QTY_MISMATCH"]);
  assert.deepEqual(x.conditionally_reconciled, ["VALUE_MISMATCH"]);
  assert.equal(x.next_best_proof, "REQ_RECONCILED_INVOICE");
});
test("quantity and arithmetic mismatch can coexist", () => {
  const x = plain(calc(scene, "31", "221.76"));
  assert.deepEqual(x.open_obligations, ["QTY_MISMATCH", "TECHNICAL_GAP", "VALUE_MISMATCH"]);
  assert.deepEqual(x.newly_exposed, ["QTY_MISMATCH"]);
});
test("untrusted values fail closed with strict bounded inputs", () => {
  for (const q of ["0", "1000", "-1", "31.5", " 28", "28e3", "NaN", ""]) {
    assert.throws(() => calc(scene, q, "221.76"), /QUANTITY_/);
  }
  for (const v of ["-0.01", "Infinity", "NaN", "1.2", "1", "1,000.00", "1000000.00", "", "1e2"]) {
    assert.throws(() => calc(scene, "28", v), /USD_AMOUNT_/);
  }
});
test("different or missing fictional source contract is rejected", () => {
  assert.throws(() => calc({}, "28", "221.76"), /VERIFIED_SYNTHETIC_SCENE_REQUIRED/);
  const copy = structuredClone(scene);
  copy.stages[1].source_lines[3] = "QUANTITY: 88 PCS";
  assert.throws(() => calc(copy, "28", "221.76"), /EXPECTED_SYNTHETIC_SCENARIO_DRIFT/);
});
test("no computed hypothesis mutates source objects", () => {
  const before = JSON.stringify(scene);
  calc(scene, "27", "213.84");
  assert.equal(JSON.stringify(scene), before);
});
