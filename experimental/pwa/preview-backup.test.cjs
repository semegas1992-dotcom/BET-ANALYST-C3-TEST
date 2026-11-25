const {test}=require("node:test"),a=require("node:assert/strict"),m=require("./preview-backup.js");
const p={sport:"nba",file_sha256:"a".repeat(64),count:9,cutoff:"2026-01-01T00:00:00Z",engine_access:false,publication:"BLOCKED",qualification:"BLOCKED"};
function store(){const x=new Map([["BET_ANALYST_C1_HISTORY","original"]]);return {getItem:k=>x.get(k)??null,setItem:(k,v)=>x.set(k,v)}}
test("round trip",()=>{const s=store();m.restore(s,m.encode([p]));a.deepEqual(m.load(s),[p]);a.equal(s.getItem("BET_ANALYST_C1_HISTORY"),"original")});
test("source stripped",()=>a.equal(m.decode(m.encode([{...p,raw:"secret"}]))[0].raw,undefined));
test("unlocked refused",()=>a.throws(()=>m.encode([{...p,engine_access:true}])));
test("duplicate refused",()=>a.throws(()=>m.encode([p,p])));
test("invalid restore preserves prior",()=>{const s=store();m.restore(s,m.encode([p]));a.throws(()=>m.restore(s,"{}"));a.deepEqual(m.load(s),[p])});
test("empty store",()=>a.deepEqual(m.load(store()),[]));
test("quota failure propagates",()=>a.throws(()=>m.restore({setItem(){throw Error("quota")}},m.encode([p]))));
