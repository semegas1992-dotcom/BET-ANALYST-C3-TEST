/* Native synthetic export verification; real archives deliberately refused. */
(function(root){
"use strict";
const base=typeof module!=="undefined"?require("./quarantine-import.js"):root.QuarantineImport;
const cryptoApi=typeof module!=="undefined"?require("node:crypto").webcrypto:root.crypto;
const enc=new TextEncoder();
function canonical(x){
 if(x===null||typeof x==="boolean")return JSON.stringify(x);
 if(typeof x==="number"){if(!Number.isSafeInteger(x))throw Error("UNSUPPORTED_NUMBER");return String(x)}
 if(typeof x==="string")return JSON.stringify(x).replace(/[\u007f-\uffff]/g,c=>"\\u"+c.charCodeAt(0).toString(16).padStart(4,"0"));
 if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";
 if(x&&typeof x==="object")return "{"+Object.keys(x).sort().map(k=>canonical(k)+":"+canonical(x[k])).join(",")+"}";
 throw Error("TYPE");
}
async function hash(s){return Array.from(new Uint8Array(await cryptoApi.subtle.digest("SHA-256",enc.encode(s))),b=>b.toString(16).padStart(2,"0")).join("")}
function keys(x,expected){if(!x||Array.isArray(x)||typeof x!=="object"||Object.keys(x).sort().join("|")!==expected.slice().sort().join("|"))throw Error("FIELDS")}
async function inspectNative(text,expected){
 if(typeof text!=="string"||enc.encode(text).length>1048576)throw Error("SIZE");
 const fileHash=await hash(text);
 if(expected!==undefined&&(!/^[a-f0-9]{64}$/.test(expected)||expected!==fileHash))throw Error("FILE_HASH");
 const d=JSON.parse(text);
 if(!d||typeof d!=="object")throw Error("SCHEMA");
 const input=d.input||d;
 const preview=base.inspect(JSON.stringify(input));
 if(d===input)return {...preview,file_sha256:fileHash,integrity:expected?"EXPECTED_HASH_MATCH":"COMPUTED_ONLY"};
 if(preview.sport!=="tennis")throw Error("NATIVE_NOT_SUPPORTED");
 keys(d,["input","output"]);
 const o=d.output;
 keys(o,["schema","origin","event","cutoff","kickoff","input_sha256","evidence","samples","audit","qualification","reasons","engine_access","publication","sha256"]);
 if(o.schema!=="D0_TENNIS_QUARANTINE_V1"||o.origin!=="synthetic"||o.engine_access!==false||o.publication!=="BLOCKED"||o.qualification!=="BLOCKED"||o.cutoff!==input.cutoff||o.kickoff!==input.kickoff||canonical(o.event)!==canonical(input.event))throw Error("LOCK_OR_LINK");
 if(await hash(canonical(input))!==o.input_sha256)throw Error("INPUT_HASH");
 const {sha256,...body}=o;
 if(await hash(canonical(body))!==sha256)throw Error("OUTPUT_HASH");
 if(!Array.isArray(o.evidence)||o.evidence.length!==input.observations.length)throw Error("EVIDENCE");
 for(let i=0;i<o.evidence.length;i++){
  const e=o.evidence[i],r=input.observations[i];
  keys(e,["id","source","event_end","available_at","captured_at","sha256"]);
  for(const k of ["id","source","event_end","available_at","captured_at"])if(e[k]!==r[k])throw Error("EVIDENCE_LINK");
  if(await hash(canonical(r))!==e.sha256)throw Error("EVIDENCE_HASH");
 }
 if(o.audit?.status!=="PASS"||o.audit.engine_access!==false||!Array.isArray(o.audit.issues)||o.audit.issues.length||!Number.isSafeInteger(o.audit.checks)||o.audit.checks<=0)throw Error("AUDIT");
 return {...preview,file_sha256:fileHash,integrity:expected?"EXPECTED_AND_INTERNAL_HASHES_MATCH":"INTERNAL_HASHES_MATCH",native:"D0_TENNIS_QUARANTINE_V1"};
}
const api={inspectNative,canonical,hash};if(typeof module!=="undefined")module.exports=api;else root.NativeImport=api;
})(globalThis);
