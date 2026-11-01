/* Real browser validation contract smoke tests (fake DOM, real WebCrypto). */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { webcrypto } = require("node:crypto");
const { TextEncoder } = require("node:util");
const root = path.resolve(__dirname, "..");
const code = fs.readFileSync(path.join(root, "docs", "app.js"), "utf8");
const model = fs.readFileSync(path.join(root, "docs", "counterfactual.js"), "utf8");
const payload = JSON.parse(fs.readFileSync(path.join(root, "docs", "data.json"), "utf8"));
function element(tag) {
  return {
    tag, textContent: "", className: "", children: [], listeners: {}, value: "",
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = [...items]; },
    setAttribute(k,v) { this[k] = v; },
    addEventListener(k,f) { this.listeners[k] = f; }
  };
}
async function run(data) {
  const nodes = new Map();
  const get = id => { if (!nodes.has(id)) nodes.set(id, element("div")); return nodes.get(id); };
  get("hyp-quantity").value = "28"; get("hyp-total").value = "235.06";
  const sandbox = {
    document: { getElementById: get, createElement: element },
    crypto: webcrypto, TextEncoder, Uint8Array,
    fetch: async () => ({
      ok: true, status: 200,
      headers: { get: () => "application/json" },
      text: async () => JSON.stringify(data)
    })
  };
  sandbox.globalThis = sandbox;
  vm.runInNewContext(model, sandbox, { timeout: 1000 });
  vm.runInNewContext(code, sandbox, { timeout: 1000 });
  await new Promise(resolve => setTimeout(resolve, 50));
  return { get, nodes };
}
test("browser validates and binds three fictional sources to pinned index", async () => {
  const { get } = await run(structuredClone(payload));
  assert.match(get("validation").textContent, /18\/18 SYNTHETIC SOURCE LITERALS VERIFIED/);
  assert.match(get("trace-hash").textContent, /VERIFIED FICTIONAL SOURCE INDEX/);
  assert.match(get("hyp-result").children.map(x => x.textContent).join(" "), /reconciled invoice/i);
  get("hyp-total").value = "221.76";
  get("hyp-apply").listeners.click();
  assert.match(get("hyp-result").children.map(x => x.textContent).join(" "), /technical specification/i);
});
test("tampered source and recomputed per-source sha still fails pinned index gate", async () => {
  const copy = structuredClone(payload);
  copy.stages[0].source_lines[2] = "PACKED QUANTITY: 999 PCS";
  const bytes = Buffer.from(copy.stages[0].source_lines.join("\n") + "\n", "utf8");
  copy.stages[0].source_sha256 = require("node:crypto").createHash("sha256").update(bytes).digest("hex");
  const { get } = await run(copy);
  assert.match(get("validation").textContent, /VERIFICATION FAILED/);
  assert.match(get("trace-hash").textContent, /SOURCE_INDEX_SHA256_MISMATCH/);
  assert.equal(get("next-proof").textContent, "NO RECOMMENDATION");
  assert.equal(get("verified-total").textContent, "0/18");
  assert.equal(get("hyp-apply").disabled, true);
  assert.equal(get("hyp-reset").disabled, true);
  assert.match(get("hyp-result").textContent, /source verification failed/);
});
test("single character edit to evidence line blocks before any decision", async () => {
  const copy = structuredClone(payload);
  copy.stages[1].source_lines[5] = "LINE TOTAL: USD 888.00";
  const { get } = await run(copy);
  assert.match(get("validation").textContent, /VERIFICATION FAILED/);
  assert.match(get("trace-hash").textContent, /SOURCE_SHA256_MISMATCH/);
  assert.equal(get("next-proof").textContent, "NO RECOMMENDATION");
});
