const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const snapshot=fs.readFileSync(path.join(__dirname,'../c3-5-snapshot.js'),'utf8');
const view=fs.readFileSync(path.join(__dirname,'../c3-5-matches-view.js'),'utf8');
const statuses=fs.readFileSync(path.join(__dirname,'../c3-6-match-status.js'),'utf8');
const statusesUrl='data:text/javascript;base64,'+Buffer.from(statuses).toString('base64');
const snapshotUrl='data:text/javascript;base64,'+Buffer.from(snapshot).toString('base64');
const viewUrl='data:text/javascript;base64,'+Buffer.from(view.replace("'./c3-5-snapshot.js'","'"+snapshotUrl+"'").replace("'./c3-6-match-status.js'","'"+statusesUrl+"'")).toString('base64');
const valid={status:'RECEIVED_UNVERIFIED',provider:'football-data.org',source_endpoint:'https://api.football-data.org/v4/competitions/PL/matches',competition:'PL',retrieved_at:'2026-11-22T10:00:00.000Z',coverage:'BASIC_MATCHES_ONLY',truncated:false,matches:[{id:12,utcDate:'2026-11-23T18:00:00Z',homeTeam:'A',awayTeam:'B',status:'SCHEDULED'}]};
test('renders only unverified matches from valid snapshot',async()=>{const {buildMatchesView}=await import(viewUrl);const r=buildMatchesView(valid,{now:Date.parse('2026-11-22T10:05:00Z')});assert.equal(r.state,'READY');assert.equal(r.matches[0].home,'A');assert.equal(r.matches[0].verified,false)});
test('stale data visibly marked',async()=>{const {buildMatchesView}=await import(viewUrl);const r=buildMatchesView(valid,{now:Date.parse('2026-11-22T11:00:00Z')});assert.equal(r.state,'STALE');assert.ok(r.warnings.includes('DONNEES_ANCIENNES'))});
test('truncated list visibly marked',async()=>{const {buildMatchesView}=await import(viewUrl);const r=buildMatchesView({...valid,truncated:true},{now:Date.parse('2026-11-22T10:05:00Z')});assert.ok(r.warnings.includes('LISTE_INCOMPLETE'))});
test('invalid snapshot cannot render matches',async()=>{const {buildMatchesView}=await import(viewUrl);const r=buildMatchesView({...valid,source_endpoint:'bad'});assert.equal(r.state,'UNAVAILABLE');assert.deepEqual(r.matches,[])});

test('C3.6 exposes classified upcoming matches',async()=>{const {buildMatchesView}=await import(viewUrl);const r=buildMatchesView(valid,{now:Date.parse('2026-11-22T10:05:00Z')});assert.equal(r.groups.UPCOMING.length,1);assert.equal(r.groups.FINISHED.length,0)});
