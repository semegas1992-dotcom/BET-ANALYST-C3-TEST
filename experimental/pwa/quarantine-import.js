/* Isolated read-only quarantine importer. No storage or network. */
(function(root){
"use strict";
const MAX=1048576, forbidden=new Set(["__proto__","constructor","prototype","odds","value","stake","ticket","parlay","profitability","simulation","probabilities"]);
function inspect(text){
 if(typeof text!=="string"||new TextEncoder().encode(text).length>MAX)throw Error("SIZE");
 const d=JSON.parse(text);let nodes=0;
 function walk(x,depth=0){
  if(++nodes>50000||depth>24)throw Error("LIMIT");
  if(x&&typeof x==="object")for(const [k,v] of Object.entries(x)){
   if(forbidden.has(k.toLowerCase()))throw Error("FORBIDDEN");
   if(k==="engine_access"&&v!==false)throw Error("LOCK");
   if(k==="publication"&&v!=="BLOCKED")throw Error("LOCK");
   walk(v,depth+1);
  }
 }
 walk(d);
 if(!d||Array.isArray(d)||d.schema!=="D0_EXPERIMENTAL_V1"||!["football","nba","tennis"].includes(d.sport)||d.origin!=="synthetic"||d.engine_access!==false)throw Error("SCHEMA");
 const time=s=>{if(typeof s!=="string"||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(s)||!Number.isFinite(Date.parse(s)))throw Error("TIME");return Date.parse(s)};
 const cutoff=time(d.cutoff);if(cutoff>=time(d.kickoff))throw Error("CUTOFF");
 if(!Array.isArray(d.observations)||!d.observations.length||d.observations.length>1000)throw Error("OBSERVATIONS");
 const ids=new Set();
 for(const o of d.observations){
  if(!o||typeof o.id!=="string"||!o.id.trim()||ids.has(o.id)||o.source!=="synthetic_fixture")throw Error("EVIDENCE");
  ids.add(o.id);
  const a=time(o.event_end),b=time(o.available_at),c=time(o.captured_at);
  if(!(a<=b&&b<=c&&c<=cutoff))throw Error("LEAKAGE");
 }
 return Object.freeze({schema:"PWA_QUARANTINE_PREVIEW_V1",sport:d.sport,cutoff:d.cutoff,kickoff:d.kickoff,count:ids.size,qualification:"BLOCKED",engine_access:false,publication:"BLOCKED",integrity:"NOT_AUTHENTICATED"});
}
const api={inspect};if(typeof module!=="undefined")module.exports=api;else root.QuarantineImport=api;
})(globalThis);
