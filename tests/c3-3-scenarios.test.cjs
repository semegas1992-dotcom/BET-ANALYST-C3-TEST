'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html','utf8');
const inline = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(x=>x[1]).find(x=>x.includes('function data()'));
assert.ok(inline,'Inline application script not found');
const elements = Object.create(null);
const fields = ['sport','event','date','cutoff','sources','force','matchup','scenarios','summary','decision','reason','scenario-a','scenario-b','scenario-c'];
for(const k of fields)elements[k]={value:''};
const storage=new Map();
const context = {
 document:{getElementById:id=>elements[id]||(elements[id]={value:'',textContent:'',className:'',replaceChildren:()=>{}})},
 C3Metadata:{cloneMarkets:x=>JSON.parse(JSON.stringify(x))},
 localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v)},
 console,Date,JSON,Array,Object,Set,Error,confirm:()=>true,
};
vm.createContext(context);
vm.runInContext(inline,context);
function base(){
 const x={sport:'FOOTBALL',event:'Équipe A – Équipe B',date:'2026-11-22',cutoff:'',sources:'D0-01',force:'Rapport de force documenté',matchup:'',scenarios:'',summary:'',decision:'ABSTENTION',reason:'Réserves explicites'};
 for(const [k,v] of Object.entries(x))elements[k].value=v;
 for(const k of ['scenario-a','scenario-b','scenario-c'])elements[k].value='';
 return x;
}
test('C3.3 structured scenarios generate compatible historical text',()=>{
 base();
 elements['scenario-a'].value='A dominant';
 elements['scenario-b'].value='B équilibré';
 elements['scenario-c'].value='C contraire';
 const d=context.data();
 assert.equal(d.c3_3_scenarios.A,'A dominant');
 assert.match(d.scenarios,/Scénario A : A dominant/);
 assert.match(d.scenarios,/Scénario C : C contraire/);
 assert.equal(context.c1Validate(d).scenarios,d.scenarios);
});
test('legacy-only scenario remains intact',()=>{
 base();elements.scenarios.value='Ancien scénario documenté';
 const d=context.data();
 assert.equal(d.scenarios,'Ancien scénario documenté');
 assert.equal(d.c3_3_scenarios.A,'');
 assert.equal(context.c1Validate(d).scenarios,'Ancien scénario documenté');
});
test('blank structured and legacy scenarios cannot be archived',()=>{
 base();const d=context.data();
 assert.throws(()=>context.c1Validate(d),/Scénarios/);
});
test('malformed optional structured scenarios are rejected',()=>{
 base();elements.scenarios.value='Scénarios historiques';
 const d=context.data();d.c3_3_scenarios={A:'A',B:42,C:'C'};
 assert.throws(()=>context.c1Validate(d),/Scénarios C3.3 invalides/);
});
test('restoring old sheet clears structured scenario fields',()=>{
 const old=base();old.markets=[];old.schema='BET_ANALYST_CONSOLIDATION_V1';old.scenarios='Ancienne projection';
 elements['scenario-a'].value='Valeur périmée';
 context.c1Fill(old);
 assert.equal(elements['scenario-a'].value,'');
 assert.equal(elements.scenarios.value,'Ancienne projection');
});

test('draft save and reopen retain all three scenarios',()=>{
 base();elements['scenario-a'].value='A rapide';elements['scenario-b'].value='B lent';elements['scenario-c'].value='C inverse';
 context.saveDraft();
 assert.ok(storage.has('BET_ANALYST_C3_3_CANDIDATE_DRAFT'));
 elements['scenario-a'].value='modifié';
 context.loadDraft();
 assert.equal(elements['scenario-a'].value,'A rapide');
 assert.equal(elements['scenario-b'].value,'B lent');
 assert.equal(elements['scenario-c'].value,'C inverse');
});
test('archive and restore retain structured scenarios',()=>{
 base();elements['scenario-a'].value='A';elements['scenario-b'].value='B';elements['scenario-c'].value='C';
 context.archiveCurrent();
 const history=JSON.parse(storage.get('BET_ANALYST_C3_3_CANDIDATE_HISTORY'));
 assert.equal(history.length,1);
 assert.equal(history[0].sheet.c3_3_scenarios.C,'C');
 elements['scenario-c'].value='altéré';
 context.restoreHistory(history[0].id);
 assert.equal(elements['scenario-c'].value,'C');
});
test('C3.2 storage keys remain untouched',()=>{
 assert.equal(storage.has('BET_ANALYST_C3_2_CANDIDATE_DRAFT'),false);
 assert.equal(storage.has('BET_ANALYST_C3_2_CANDIDATE_HISTORY'),false);
});
