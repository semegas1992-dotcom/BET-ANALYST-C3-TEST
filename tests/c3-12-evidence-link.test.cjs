const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'../preview-c3-7');
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
const source=read('c3-12-evidence-link.js');
const snapshotSource=read('c3-5-snapshot.js');
const evidenceSource=read('c3-11-kraft-evidence.js');
const now=Date.parse('2026-11-23T08:00:00Z');
const fixture=()=>({schema:'BET_ANALYST_MATCH_SNAPSHOT_V1',status:'RECEIVED_UNVERIFIED',provider:'football-data.org',source_endpoint:'https://api.football-data.org/v4/competitions/PL/matches',competition:'PL',retrieved_at:new Date(now).toISOString(),coverage:'BASIC_MATCHES_ONLY',truncated:false,matches:[{id:123,utcDate:'2026-11-24T20:00:00Z',homeTeam:'Fictif A',awayTeam:'Fictif B',status:'SCHEDULED'}]});
const dossier=()=>({schema:'BET_ANALYST_KRAFT_EVIDENCE_V1',match_id:'123',created_at:'2026-11-23T08:00:00Z',evidence:[{id:'missing-1',domain:'TEAM_FORM',state:'MISSING',value:null}]});
async function link(s,d){
 // Import the actual source modules through data URLs, replacing only relative import specifiers.
 const a='data:text/javascript;base64,'+Buffer.from(snapshotSource).toString('base64');
 const b='data:text/javascript;base64,'+Buffer.from(evidenceSource).toString('base64');
 const rewritten=source.replace("'./c3-5-snapshot.js'",JSON.stringify(a)).replace("'./c3-11-kraft-evidence.js'",JSON.stringify(b));
 const c='data:text/javascript;base64,'+Buffer.from(rewritten).toString('base64');
 return (await import(c)).linkMatchEvidence(s,d,{now});
}
test('C3.12: liaison exacte fictive, jamais validation KRAFT',async()=>{const r=await link(fixture(),dossier());assert.equal(r.linked,true);assert.equal(r.status,'LINKED_UNVERIFIED');assert.equal(r.analysis_readiness,'BLOCKED');assert.equal(r.verified,false);assert.equal(r.evidence_count,1);assert.equal(r.match.id,'123')});
test('C3.12: mauvais identifiant refusé',async()=>{const d=dossier();d.match_id='124';const r=await link(fixture(),d);assert.equal(r.linked,false);assert.ok(r.errors.includes('MATCH_ID_NOT_FOUND'))});
test('C3.12: dossier invalide refusé',async()=>{const d=dossier();d.evidence[0].value='inventé';const r=await link(fixture(),d);assert.equal(r.linked,false);assert.ok(r.errors.includes('EVIDENCE_DOSSIER_INVALID'))});
test('C3.12: instantané invalide refusé',async()=>{const s=fixture();s.matches[0].homeTeam='';const r=await link(s,dossier());assert.equal(r.linked,false);assert.ok(r.errors.includes('MATCH_SNAPSHOT_INVALID'))});
test('C3.12: comparaison exacte, pas de correspondance partielle',async()=>{const d=dossier();d.match_id='12';assert.equal((await link(fixture(),d)).linked,false)});
test('C3.12: aucune requête réseau',()=>{assert.doesNotMatch(source,/\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket/)});
