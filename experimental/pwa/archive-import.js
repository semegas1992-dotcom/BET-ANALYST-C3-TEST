/* Read-only native archive adapter. Byte hash is the cross-language contract. */
(function(root){
"use strict";
const api=typeof module!=="undefined"?require("./native-import.js"):root.NativeImport;
const specs={
 D0_ENRICHED_EXPERIMENTAL_V1:{sport:"football",publication:"BLOCKED_UPSTREAM_RIGHTS_NOT_CONFIRMED"},
 BET_ANALYST_NBA_BATCH_V4:{sport:"nba",publication:"BLOCKED_RIGHTS_NOT_CONFIRMED"}
};
function parseStrict(s){
 let i=0,n=0;
 const ws=()=>{while(/[\x20\t\r\n]/.test(s[i]||"x"))i++};
 function val(depth){
  if(++n>250000||depth>32)throw Error("LIMIT");ws();
  const c=s[i];
  if(c==='"'){const start=i++;while(i<s.length){if(s[i]==="\\"){i+=2;continue}if(s[i++]==='"')return JSON.parse(s.slice(start,i))}throw Error("STRING")}
  if(c==="{"||c==="["){i++;ws();const obj=c==="{",end=obj?"}":"]",a=obj?Object.create(null):[];if(s[i]===end){i++;return a}
   while(true){ws();if(obj){const k=val(depth+1);if(typeof k!=="string"||Object.hasOwn(a,k)||["__proto__","constructor","prototype"].includes(k.toLowerCase()))throw Error("KEY");ws();if(s[i++]!==":")throw Error("COLON");a[k]=val(depth+1)}else a.push(val(depth+1));ws();if(s[i]===end){i++;return a}if(s[i++]!==",")throw Error("COMMA")}
  }
  const m=/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(s.slice(i));if(!m)throw Error("TOKEN");i+=m[0].length;const v=JSON.parse(m[0]);if(typeof v==="number"&&!Number.isFinite(v))throw Error("NUMBER");return v;
 }
 const d=val(0);ws();if(i!==s.length)throw Error("TRAILING");return d;
}
async function inspectArchive(text,expected){
 if(typeof text!=="string"||new TextEncoder().encode(text).length>1048576)throw Error("SIZE");
 const d=parseStrict(text),h=await api.hash(text);
 if(typeof expected!=="string"||!/^[a-f0-9]{64}$/.test(expected)||h!==expected)throw Error("TRUSTED_FILE_HASH_REQUIRED");
 const spec=specs[d.schema];
 if(!spec){
  if(d.input?.sport!=="tennis"||d.output?.schema!=="D0_TENNIS_QUARANTINE_V1")return api.inspectNative(text,expected);
  if(d.input.engine_access!==false||d.output.engine_access!==false||d.output.publication!=="BLOCKED"||d.output.qualification!=="BLOCKED"||d.output.cutoff!==d.input.cutoff||d.output.kickoff!==d.input.kickoff||d.output.audit?.status!=="PASS"||d.output.audit.issues?.length!==0)throw Error("TENNIS_LOCK");
  const base=typeof module!=="undefined"?require("./quarantine-import.js"):root.QuarantineImport;
  const p=base.inspect(JSON.stringify(d.input));
  return {...p,file_sha256:h,native:d.output.schema,integrity:"EXPECTED_FILE_HASH_MATCH",internal_hashes:"NOT_RECOMPUTED"};
 }
 if(d.engine_access!==false||d.publication!==spec.publication||!Array.isArray(d.dossiers)||!d.dossiers.length||typeof d.cutoff!=="string"||!Number.isFinite(Date.parse(d.cutoff)))throw Error("SCHEMA");
 const forbidden=new Set(["odds","stake","ticket","parlay","profitability","probabilities"]);
 function walk(x){if(x&&typeof x==="object")for(const [k,v] of Object.entries(x)){if(forbidden.has(k.toLowerCase())||(k==="engine_access"&&v!==false)||(k==="publication"&&v!==spec.publication&&v!=="BLOCKED"))throw Error("LOCK");walk(v)}}
 walk(d);
 const ids=new Set();
 for(const r of d.dossiers){
  const id=spec.sport==="football"?r.id:r.event?.id;
  const kickoff=spec.sport==="football"?r.kickoff:r.event?.tipoff;
  if(r.engine_access!==false||id==null||ids.has(String(id))||!Number.isFinite(Date.parse(kickoff))||Date.parse(kickoff)<=Date.parse(d.cutoff))throw Error("DOSSIER");
  ids.add(String(id));
  if(spec.sport==="football"){if(!r.sides||typeof r.competition!=="string"||!/^[a-f0-9]{64}$/.test(r.source_hash))throw Error("FOOTBALL")}
  else if(!Array.isArray(r.history_refs)||r.history_refs.length!==2||!r.history_refs.every(k=>Object.hasOwn(d.histories||{},k)))throw Error("NBA_HISTORY");
 }
 if(spec.sport==="football"?d.audit?.pass!==true:d.audit?.status!=="PASS")throw Error("AUDIT");
 if(!Array.isArray(d.audit.issues)||d.audit.issues.length)throw Error("AUDIT_ISSUES");
 return Object.freeze({schema:"PWA_QUARANTINE_PREVIEW_V1",sport:spec.sport,native:d.schema,cutoff:d.cutoff,count:ids.size,file_sha256:h,integrity:"EXPECTED_FILE_HASH_MATCH",internal_hashes:"NOT_RECOMPUTED",qualification:"BLOCKED",engine_access:false,publication:"BLOCKED"});
}
const out={inspectArchive,parseStrict};if(typeof module!=="undefined")module.exports=out;else root.ArchiveImport=out;
})(globalThis);
