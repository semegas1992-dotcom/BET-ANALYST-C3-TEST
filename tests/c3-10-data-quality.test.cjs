// C3.10-D — Tests hors réseau, uniquement sur données fictives.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../preview-c3-7/c3-5-snapshot.js'),'utf8');
const moduleUrl = 'data:text/javascript;base64,'+Buffer.from(source).toString('base64');
const now = Date.parse('2026-11-23T08:00:00.000Z');
const sample = () => ({
 schema:'BET_ANALYST_MATCH_SNAPSHOT_V1',status:'RECEIVED_UNVERIFIED',
 provider:'football-data.org',
 source_endpoint:'https://api.football-data.org/v4/competitions/PL/matches',
 competition:'PL',retrieved_at:new Date(now).toISOString(),
 coverage:'BASIC_MATCHES_ONLY',truncated:false,
 matches:[{id:1,utcDate:'2026-11-24T20:00:00Z',homeTeam:'Équipe fictive A',awayTeam:'Équipe fictive B',status:'SCHEDULED'}]
});
async function validate(data,options={}) {
 const {validateSnapshot} = await import(moduleUrl);
 return validateSnapshot(data,{now,...options});
}
test('C3.10-D: snapshot fictif valide reste affichable mais non vérifié',async()=>{
 const result=await validate(sample());
 assert.equal(result.usable,true);
 assert.equal(result.verified,false);
 assert.equal(result.matches.length,1);
});
test('C3.10-D: objet et JSON mal formés refusés',async()=>{
 assert.equal((await validate(null)).usable,false);
 assert.throws(()=>JSON.parse('{invalid'));
});
test('C3.10-D: identifiants en double refusés',async()=>{
 const s=sample();s.matches.push({...s.matches[0]});
 const result=await validate(s);
 assert.equal(result.usable,false);
 assert.ok(result.errors.includes('DUPLICATE_MATCH_IDS'));
});
test('C3.10-D: champs obligatoires absents refusés',async()=>{
 const s=sample();delete s.matches[0].homeTeam;
 const result=await validate(s);
 assert.equal(result.usable,false);
 assert.ok(result.errors.includes('INVALID_MATCH_FIELDS'));
});
test('C3.10-D: source et compétition incohérentes refusées',async()=>{
 const s=sample();s.competition='BL1';
 const result=await validate(s);
 assert.equal(result.usable,false);
 assert.ok(result.errors.includes('SOURCE_COMPETITION_MISMATCH'));
});
test('C3.10-D: date de collecte future refusée',async()=>{
 const s=sample();s.retrieved_at=new Date(now+60_000).toISOString();
 const result=await validate(s);
 assert.equal(result.usable,false);
 assert.ok(result.errors.includes('FUTURE_TIMESTAMP'));
});
test('C3.10-D: instantané ancien signalé, sans fausse vérification',async()=>{
 const s=sample();s.retrieved_at=new Date(now-16*60_000).toISOString();
 const result=await validate(s);
 assert.equal(result.usable,true);
 assert.equal(result.freshness,'STALE');
 assert.equal(result.verified,false);
});
test('C3.10-D: plus de 100 matchs refusés',async()=>{
 const s=sample();s.matches=Array.from({length:101},(_,i)=>({...s.matches[0],id:i+1}));
 const result=await validate(s);
 assert.equal(result.usable,false);
 assert.ok(result.errors.includes('INVALID_MATCHES'));
});
test('C3.10-D: contrôle KRAFT bloquant présent dans le modèle',()=>{
 const view=fs.readFileSync(path.join(__dirname,'../preview-c3-7/c3-5-matches-view.js'),'utf8');
 assert.match(view,/analysis_readiness:'BLOCKED'/);
 assert.match(view,/missing_for_kraft:/);
 assert.match(view,/SOURCE_VERIFICATION/);
});
test('C3.10-D: interface affiche le statut KRAFT et conserve la recherche',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../preview-c3-7/index.html'),'utf8');
 assert.match(html,/id="kraft-audit"/);
 assert.match(html,/renderKraft\(view\)/);
 assert.match(html,/id="search"/);
 assert.match(html,/selected\.length\+' rencontre\(s\) affichée\(s\) sur '\+all\.length/);
});

test('C3.10-D: erreur JSON efface également le statut KRAFT précédent',()=>{
 const html=fs.readFileSync(path.join(__dirname,'../preview-c3-7/index.html'),'utf8');
 assert.match(html,/catch\{currentView=null;renderKraft\(null\);renderMatches\(\);status\.textContent='Fichier JSON illisible\.'/);
 assert.match(html,/catch\{currentView=null;renderKraft\(null\);renderMatches\(\);status\.textContent='Erreur pendant la validation du fichier\.'/);
});
