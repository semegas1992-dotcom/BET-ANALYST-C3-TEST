'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const audit=require('../c3-3-coherence.js');
test('trois scénarios distincts ne sont pas validés sportivement',()=>{
 const x=audit.inspect({A:'Domination A',B:'Match serré',C:'Domination B'});
 assert.equal(x.status,'REVUE_HUMAINE_REQUISE');
 assert.equal(x.validated_sportively,false);
 assert.equal(x.contradictions_verified,false);
});
test('champ absent identifié sans inventer de scénario',()=>{
 const x=audit.inspect({A:'A',B:'  ',C:'C'});
 assert.deepEqual(x.missing,['B']);
 assert.equal(x.status,'INCOMPLET');
});
test('doublon textuel signalé sans conclure à une contradiction',()=>{
 const x=audit.inspect({A:' Match fermé ',B:'match fermé',C:'Match ouvert'});
 assert.deepEqual(x.identical,[['A','B']]);
 assert.equal(x.status,'A_EXAMINER');
 assert.equal(x.contradictions_verified,false);
});
test('formats invalides refusés',()=>{
 assert.throws(()=>audit.inspect({A:'A',B:3,C:'C'}),/non conformes/);
});
test('aucune probabilité calculée',()=>{
 const x=audit.inspect({A:'A 60 %',B:'B 30 %',C:'C 10 %'});
 assert.equal(x.probabilities_calculated,false);
});
