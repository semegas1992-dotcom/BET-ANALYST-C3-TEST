const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../preview-c3-7/c3-11-kraft-evidence.js'),'utf8');
const moduleUrl='data:text/javascript;base64,'+Buffer.from(source).toString('base64');
const base=()=>({schema:'BET_ANALYST_KRAFT_EVIDENCE_V1',match_id:'FICTIVE-001',created_at:'2026-11-23T08:00:00Z',evidence:[]});
const verified=(domain,id)=>({id,domain,state:'VERIFIED',value:'Exemple fictif',source:'source fictive locale',observed_at:'2026-11-23T08:00:00Z',verification_note:'Contrôle fictif, ne constitue pas une preuve réelle'});
async function audit(s){const m=await import(moduleUrl);return m.validateKraftEvidence(s)}
test('C3.11: dossier vide reste bloqué',async()=>{const a=await audit(base());assert.equal(a.valid,true);assert.equal(a.analysis_readiness,'BLOCKED');assert.equal(a.missing_domains.length,5)});
test('C3.11: preuve vérifiée requiert provenance',async()=>{const s=base();s.evidence=[{id:'a',domain:'TEAM_FORM',state:'VERIFIED',value:1}];assert.ok((await audit(s)).errors.includes('VERIFICATION_EVIDENCE_REQUIRED_0'))});
test('C3.11: hypothèse requiert justification',async()=>{const s=base();s.evidence=[{id:'a',domain:'TEAM_FORM',state:'HYPOTHESIS',value:1}];assert.ok((await audit(s)).errors.includes('HYPOTHESIS_RATIONALE_REQUIRED_0'))});
test('C3.11: valeur manquante doit être null',async()=>{const s=base();s.evidence=[{id:'a',domain:'TEAM_FORM',state:'MISSING',value:1}];assert.ok((await audit(s)).errors.includes('MISSING_MUST_HAVE_NULL_VALUE_0'))});
test('C3.11: doublons refusés',async()=>{const s=base();s.evidence=[verified('TEAM_FORM','a'),verified('TEAM_STATISTICS','a')];assert.equal((await audit(s)).valid,false)});
test('C3.11: cinq domaines présents ne débloquent pas automatiquement KRAFT',async()=>{const s=base();s.evidence=['TEAM_FORM','TEAM_STATISTICS','SQUAD_AVAILABILITY','TACTICAL_CONTEXT','PLAYER_STATISTICS'].map((d,i)=>verified(d,'a'+i));const a=await audit(s);assert.equal(a.valid,true);assert.equal(a.missing_domains.length,0);assert.equal(a.analysis_readiness,'BLOCKED')});
test('C3.11: date sans fuseau refusée',async()=>{const s=base();s.created_at='2026-11-23T08:00:00';assert.equal((await audit(s)).valid,false)});
