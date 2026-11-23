const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../c3-5-snapshot-builder.js'),'utf8');
const url='data:text/javascript;base64,'+Buffer.from(source).toString('base64');
test('creates snapshot from basic match data without inventing fields',async()=>{const {createMatchSnapshot}=await import(url);const r=createMatchSnapshot({matches:[{id:1,utcDate:'2026-11-24T20:00:00Z',homeTeam:{name:'A'},awayTeam:{name:'B'}}]},{competition:'PL',retrievedAt:'2026-11-22T20:00:00Z'});assert.equal(r.status,'RECEIVED_UNVERIFIED');assert.equal(r.matches[0].homeTeam,'A');assert.equal(r.matches[0].status,null);assert.equal(r.source_endpoint,'https://api.football-data.org/v4/competitions/PL/matches')});
test('invalid provider response is rejected',async()=>{const {createMatchSnapshot}=await import(url);assert.throws(()=>createMatchSnapshot({error:'bad'},{competition:'PL'}),/INVALID_PROVIDER_RESPONSE/)});
test('truncation is explicitly flagged',async()=>{const {createMatchSnapshot}=await import(url);const r=createMatchSnapshot({matches:Array.from({length:101},(_,i)=>({id:i+1,utcDate:'2026-11-24T20:00:00Z',homeTeam:{name:'A'},awayTeam:{name:'B'}}))},{competition:'PL'});assert.equal(r.truncated,true);assert.equal(r.matches.length,100)});
test('competition is validated',async()=>{const {createMatchSnapshot}=await import(url);assert.throws(()=>createMatchSnapshot({matches:[]},{competition:'../'}),/INVALID_COMPETITION/)});

test('incomplete match data is rejected before snapshot creation',async()=>{const {createMatchSnapshot}=await import(url);assert.throws(()=>createMatchSnapshot({matches:[{id:1,homeTeam:{name:'A'}}]},{competition:'PL'}),/INCOMPLETE_MATCH_DATA/)});

test('C3.6 prioritizes future fixtures when provider returns over 100 matches',async()=>{
 const {createMatchSnapshot}=await import(url);
 const match=(id,status,date)=>({id,status,utcDate:date,homeTeam:{name:'A'},awayTeam:{name:'B'}});
 const old=Array.from({length:100},(_,i)=>match(i+1,'FINISHED','2026-11-01T20:00:00Z'));
 const next=match(101,'SCHEDULED','2026-11-25T20:00:00Z');
 const r=createMatchSnapshot({matches:[...old,next]},{competition:'PL',retrievedAt:'2026-11-23T06:00:00Z'});
 assert.equal(r.matches[0].id,101);
 assert.equal(r.truncated,true);
 assert.equal(r.matches.length,100);
});
