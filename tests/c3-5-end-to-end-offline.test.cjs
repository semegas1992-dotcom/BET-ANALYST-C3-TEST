const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
const data=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const snapshotUrl=data(read('c3-5-snapshot.js'));
const builderUrl=data(read('c3-5-snapshot-builder.js'));
const statusUrl=data(read('c3-6-match-status.js'));
const viewUrl=data(read('c3-5-matches-view.js').replace("'./c3-5-snapshot.js'","'"+snapshotUrl+"'").replace("'./c3-6-match-status.js'","'"+statusUrl+"'"));
const raw={matches:[{id:42,utcDate:'2026-11-24T20:00:00Z',status:'SCHEDULED',homeTeam:{name:'Équipe A'},awayTeam:{name:'Équipe B'}}]};
test('complete offline pipeline: provider response to validated read-only display',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);
 const {buildMatchesView}=await import(viewUrl);
 const snapshot=createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-22T20:00:00Z'});
 const view=buildMatchesView(snapshot,{now:Date.parse('2026-11-22T20:05:00Z')});
 assert.equal(view.state,'READY');assert.equal(view.matches.length,1);assert.equal(view.groups.UPCOMING.length,1);
 assert.equal(view.matches[0].home,'Équipe A');assert.equal(view.matches[0].away,'Équipe B');
 assert.equal(view.verified,false);assert.equal(view.matches[0].verified,false);
});
test('offline pipeline never masks an expired snapshot',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);const {buildMatchesView}=await import(viewUrl);
 const snapshot=createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-22T20:00:00Z'});
 const view=buildMatchesView(snapshot,{now:Date.parse('2026-11-22T22:00:00Z')});
 assert.equal(view.state,'STALE');assert.ok(view.warnings.includes('DONNEES_ANCIENNES'));
});

test('C3.8 actual JSON serialization round-trip remains readable in Android preview model',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);
 const {buildMatchesView}=await import(viewUrl);
 const generated=createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-23T06:00:00Z'});
 const downloaded=JSON.parse(JSON.stringify(generated));
 const view=buildMatchesView(downloaded,{now:Date.parse('2026-11-23T06:05:00Z')});
 assert.equal(downloaded.schema,'BET_ANALYST_MATCH_SNAPSHOT_V1');
 assert.equal(view.state,'READY');
 assert.equal(view.groups.UPCOMING.length,1);
 assert.equal(view.matches[0].id,'42');
 assert.equal(view.verified,false);
});
test('C3.8 serialized snapshot imported after 15 minutes visibly warns of age',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);
 const {buildMatchesView}=await import(viewUrl);
 const file=JSON.stringify(createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-23T06:00:00Z'}));
 const view=buildMatchesView(JSON.parse(file),{now:Date.parse('2026-11-23T06:16:00Z')});
 assert.equal(view.state,'STALE');
 assert.ok(view.warnings.includes('DONNEES_ANCIENNES'));
});

test('C3.8 fictional five-match fixture groups all statuses without claiming verification',async()=>{
 const {buildMatchesView}=await import(viewUrl);
 const fixture=JSON.parse(read('tests/fixtures/c3-8-fictional-multi-match.json'));
 const view=buildMatchesView(fixture,{now:Date.parse('2026-11-23T06:05:00Z')});
 assert.equal(view.state,'READY');
 assert.equal(view.matches.length,5);
 assert.equal(view.groups.UPCOMING.length,2);
 assert.equal(view.groups.LIVE.length,1);
 assert.equal(view.groups.FINISHED.length,1);
 assert.equal(view.groups.OTHER.length,1);
 assert.equal(view.verified,false);
 assert.ok(view.matches.every(m=>m.verified===false));
});
