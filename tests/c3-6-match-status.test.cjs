const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../c3-6-match-status.js'),'utf8');
const url='data:text/javascript;base64,'+Buffer.from(source).toString('base64');
test('C3.6 statuses remain conservative and groups are sorted',async()=>{
 const {classifyMatchStatus,groupMatchesByStatus}=await import(url);
 assert.equal(classifyMatchStatus('SCHEDULED'),'UPCOMING');
 assert.equal(classifyMatchStatus('TIMED'),'UPCOMING');
 assert.equal(classifyMatchStatus('IN_PLAY'),'LIVE');
 assert.equal(classifyMatchStatus('FINISHED'),'FINISHED');
 assert.equal(classifyMatchStatus('POSTPONED'),'OTHER');
 assert.equal(classifyMatchStatus('UNRECOGNIZED'),'UNKNOWN');
 const groups=groupMatchesByStatus([{status:'SCHEDULED',date_utc:'2026-12-02T00:00:00Z'},{status:'SCHEDULED',date_utc:'2026-12-01T00:00:00Z'},{status:'UNKNOWN'}]);
 assert.equal(groups.UPCOMING.length,2);
 assert.equal(groups.UPCOMING[0].date_utc,'2026-12-01T00:00:00Z');
 assert.equal(groups.UNKNOWN.length,1);
});
