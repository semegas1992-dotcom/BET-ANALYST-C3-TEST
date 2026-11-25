/* Isolated preview-only backup; never stores source archives. */
(function(root){
"use strict";
const KEY="BET_ANALYST_EXPERIMENTAL_QUARANTINE_PREVIEWS_V1";
const fields=["sport","file_sha256","count","cutoff","engine_access","publication","qualification"];
function validate(p){
 if(!p||typeof p!=="object"||!["football","nba","tennis"].includes(p.sport)||!/^[a-f0-9]{64}$/.test(p.file_sha256)||!Number.isSafeInteger(p.count)||p.count<1||p.count>1000||typeof p.cutoff!=="string"||!Number.isFinite(Date.parse(p.cutoff))||p.engine_access!==false||p.publication!=="BLOCKED"||p.qualification!=="BLOCKED")throw Error("PREVIEW");
 return Object.fromEntries(fields.map(k=>[k,p[k]]));
}
function decode(text){
 if(typeof text!=="string"||new TextEncoder().encode(text).length>131072)throw Error("SIZE");
 const d=JSON.parse(text);
 if(d?.schema!=="QUARANTINE_PREVIEW_BACKUP_V1"||!Array.isArray(d.previews)||d.previews.length>100)throw Error("SCHEMA");
 const seen=new Set();
 return d.previews.map(p=>{const v=validate(p);if(seen.has(v.file_sha256))throw Error("DUPLICATE");seen.add(v.file_sha256);return v});
}
function encode(previews){const text=JSON.stringify({schema:"QUARANTINE_PREVIEW_BACKUP_V1",previews:previews.map(validate)});decode(text);return text}
function restore(storage,text){const clean=encode(decode(text));storage.setItem(KEY,clean);return decode(clean)}
function load(storage){const s=storage.getItem(KEY);return s===null?[]:decode(s)}
const api={KEY,validate,decode,encode,restore,load};if(typeof module!=="undefined")module.exports=api;else root.PreviewBackup=api;
})(globalThis);
