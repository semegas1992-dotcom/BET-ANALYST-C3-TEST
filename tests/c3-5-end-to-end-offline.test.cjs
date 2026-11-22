const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
const data=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const snapshotUrl=data(read('c3-5-snapshot.js'));
const builderUrl=data(read('c3-5-snapshot-builder.js'));
const viewUrl=data(read('c3-5-matches-view.js').replace("'./c3-5-snapshot.js'","'"+snapshotUrl+"'"));
const raw={matches:[{id:42,utcDate:'2026-11-24T20:00:00Z',status:'SCHEDULED',homeTeam:{name:'Équipe A'},awayTeam:{name:'Équipe B'}}]};
test('complete offline pipeline: provider response to validated read-only display',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);
 const {buildMatchesView}=await import(viewUrl);
 const snapshot=createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-22T20:00:00Z'});
 const view=buildMatchesView(snapshot,{now:Date.parse('2026-11-22T20:05:00Z')});
 assert.equal(view.state,'READY');assert.equal(view.matches.length,1);
 assert.equal(view.matches[0].home,'Équipe A');assert.equal(view.matches[0].away,'Équipe B');
 assert.equal(view.verified,false);assert.equal(view.matches[0].verified,false);
});
test('offline pipeline never masks an expired snapshot',async()=>{
 const {createMatchSnapshot}=await import(builderUrl);const {buildMatchesView}=await import(viewUrl);
 const snapshot=createMatchSnapshot(raw,{competition:'PL',retrievedAt:'2026-11-22T20:00:00Z'});
 const view=buildMatchesView(snapshot,{now:Date.parse('2026-11-22T22:00:00Z')});
 assert.equal(view.state,'STALE');assert.ok(view.warnings.includes('DONNEES_ANCIENNES'));
});
