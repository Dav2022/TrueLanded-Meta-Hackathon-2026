"use strict";
/* DF-SEC-001: unchanged historical bytes, fake DOM, real WebCrypto; no network. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { webcrypto, createHash } = require("node:crypto");
const { TextDecoder } = require("node:util");
const root = path.resolve(__dirname, "..");
const script = fs.readFileSync(path.join(root, "docs/adjudication.js"), "utf8");
const original = fs.readFileSync(path.join(root, "docs/adjudication-data.json"));
const payload = JSON.parse(original.toString("utf8"));
const pinned = "9fe6e2cd2fd640d28baaef5a68ad7af1c6c34e2d90a62b48db8a5b6364c612ea";
function changed(mutate) {
  const copy = structuredClone(payload);
  mutate(copy);
  return Buffer.from(JSON.stringify(copy) + "\n");
}
function element() {
  return {value:"", textContent:"STALE RESULT", className:"", disabled:false, children:[], listeners:{},
    append(...items) {this.children.push(...items); if (!this.value && items.length) this.value=items[0].value;},
    replaceChildren(...items) {this.children=[...items];this.textContent="";if(!items.length)this.value="";},
    addEventListener(name, callback) {this.listeners[name]=callback;}};
}
async function run(bytes=original, options={}) {
  const nodes = new Map();
  const get = id => {if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};
  for (const id of ["lab-case","lab-inputs","lab-delta","lab-excluded","lab-lineage","lab-integrity"]) get(id);
  get("lab-case").value="";
  const calls=[];
  const sandbox={document:{getElementById:get,createElement:element},Uint8Array,TextDecoder,
    crypto:options.crypto===undefined ? webcrypto : options.crypto,
    fetch:async(url,init)=>{
      calls.push({url,init});
      if(options.networkError)throw Error("offline");
      const buffer=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
      return {ok:options.ok!==false,status:options.ok===false?404:200,
        headers:{get:name=>name.toLowerCase()==="content-type"?(options.type||"application/json; charset=utf-8"):null},
        arrayBuffer:async()=>buffer,text:async()=>bytes.toString("utf8")};
    }};
  // Defense-in-depth checks only: emulate an authorized future release pin in memory.
  // The normal adversarial tests never change the production pin or hash implementation.
  let code=options.code||script;
  if(options.repin) {
    assert.equal(code.split(pinned).length,2,"the production SHA must occur exactly once");
    code=code.replace(pinned,createHash("sha256").update(bytes).digest("hex"));
  }
  const completion=vm.runInNewContext(code,sandbox,{timeout:1000});
  assert.ok(completion && typeof completion.then==="function","script must expose its initialization completion");
  await completion;
  return {get,calls};
}
function refused(result) {
  assert.match(result.get("lab-validation").textContent,/REPLAY REFUSED/);
  assert.equal(result.get("lab-validation").className,"validation fail");
  assert.equal(result.get("lab-case").disabled,true);
  assert.equal(result.get("lab-case").children.length,0);
  assert.equal(result.get("lab-inputs").children.length,0);
  assert.equal(result.get("lab-status").textContent,"NO RECOMMENDATION");
  for(const id of ["lab-delta","lab-excluded","lab-lineage"]) assert.equal(result.get(id).textContent,"");
  assert.equal(result.get("lab-integrity").textContent,"INTEGRITY NOT VERIFIED");
}
test("DF-SEC-001: authentic historical bytes verify and all 30 outputs remain unchanged",async()=>{
  assert.equal(createHash("sha256").update(original).digest("hex"),pinned);
  const result=await run();
  assert.match(result.get("lab-validation").textContent,/30 \/ 30 SYNTHETIC EXPECTED VERDICTS/);
  assert.equal(result.get("lab-case").disabled,false);
  assert.equal(result.get("lab-case").children.length,30);
  assert.ok(result.get("lab-integrity").textContent.includes(pinned));
  assert.equal(result.calls.length,1);
  assert.equal(result.calls[0].url,"adjudication-data.json");
  assert.equal(result.calls[0].init.credentials,"omit");
  assert.equal(result.calls[0].init.redirect,"error");
  for(const c of payload.cases) {
    result.get("lab-case").value=c.id;
    result.get("lab-case").listeners.change();
    assert.equal(result.get("lab-status").textContent,c.output.status.replaceAll("_"," "));
    const expected=c.output.difference===null?"No documentary arithmetic permitted.":
      `Declared: ${c.output.declared} packages · Inspected: ${c.output.inspected} packages · Difference: ${c.output.difference} packages for review.`;
    assert.equal(result.get("lab-delta").textContent,expected);
    assert.equal(result.get("lab-inputs").children.length,c.inputs.length);
  }
});
const mutations=[
  ["modified output.status",d=>{d.cases[0].output.status="FORGED_APPROVED";}],
  ["modified output.difference",d=>{d.cases[0].output.difference=987654321;}],
  ["altered matches_expected",d=>{d.cases[0].matches_expected=false;}],
  ["removed case",d=>{d.cases.pop();}],
  ["appended duplicate case",d=>{d.cases.push(structuredClone(d.cases[0]));}],
  ["duplicate replacing a case at count 30",d=>{d.cases[1]=structuredClone(d.cases[0]);}],
  ["modified engine identifier",d=>{d.engine_sha256="0".repeat(64);}],
  ["modified fixture identifier",d=>{d.fixture_sha256="0".repeat(64);}]
];
for(const [name,mutate] of mutations) test(`DF-SEC-001 rejects ${name}`,async()=>refused(await run(changed(mutate))));
for(const [name,bytes] of [
  ["truncated JSON",original.subarray(0,original.length-20)],
  ["invalid JSON",Buffer.from("{invalid}")],
  ["trailing byte",Buffer.concat([original,Buffer.from(" ")])],
  ["UTF-8 BOM",Buffer.concat([Buffer.from([239,187,191]),original])],
  ["invalid UTF-8",Buffer.from([255,254,0,123])],
  ["oversized response",Buffer.alloc(80001,32)]
]) test(`DF-SEC-001 rejects ${name}`,async()=>refused(await run(bytes)));
test("DF-SEC-001 fails closed without WebCrypto",async()=>{
  const result=await run(original,{crypto:null});refused(result);assert.equal(result.calls.length,0);
});
test("DF-SEC-001 fails closed when SHA-256 fails",async()=>refused(await run(original,{crypto:{subtle:{digest:async()=>{throw Error("digest unavailable");}}}})));
test("DF-SEC-001 fails closed on fetch failure",async()=>refused(await run(original,{networkError:true})));
test("DF-SEC-001 fails closed on HTTP failure",async()=>refused(await run(original,{ok:false})));
test("DF-SEC-001 refuses HTML content type",async()=>refused(await run(original,{type:"text/html"})));
test("DF-SEC-001 refuses unknown selection and cannot restore stale verified results",async()=>{
  const result=await run();
  result.get("lab-case").value="UNKNOWN_CASE";
  result.get("lab-case").listeners.change();refused(result);
  result.get("lab-case").value=payload.cases[0].id;
  result.get("lab-case").listeners.change();refused(result);
});
const structural=[
  ...mutations,
  ["wrong mode",d=>{d.mode="LIVE_INFERENCE";}],
  ["string meta_calls",d=>{d.meta_calls="0";}],
  ["forged legal authorization",d=>{d.legal_action_authorized=true;}],
  ["unknown top-level key",d=>{d.unexpected=true;}],
  ["null output",d=>{d.cases[0].output=null;}],
  ["string difference",d=>{d.cases[0].output.difference="3";}],
  ["boolean evidence count",d=>{d.cases[0].output.evidence_nodes=true;}],
  ["negative declared count",d=>{d.cases[0].output.declared=-68;}],
  ["arithmetic mismatch",d=>{d.cases[0].output.inspected=64;}],
  ["unexpected input value type",d=>{d.cases[0].inputs[0].value={html:"<b>forged</b>"};}],
  ["unknown input key",d=>{d.cases[0].inputs[0].approved=true;}],
  ["missing scope flag",d=>{delete d.human_review_required;}],
  ["string matches_expected",d=>{d.cases[0].matches_expected="true";}],
  ["reordered cases",d=>{[d.cases[0],d.cases[1]]=[d.cases[1],d.cases[0]];}]
];
for(const [name,mutate] of structural) test(`DF-SEC-001 schema defense after hypothetical repin: ${name}`,
  async()=>refused(await run(changed(mutate),{repin:true})));
for(const [name,bytes] of [["invalid JSON",Buffer.from("{invalid}")],["invalid UTF-8",Buffer.from([255,254,0,123])]])
  test(`DF-SEC-001 strict decoding after hypothetical repin: ${name}`,async()=>refused(await run(bytes,{repin:true})));
