'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {inspect}=require('../c3-4-market-comparison.js');
const m=(id,threshold,category='COLLECTIF')=>({id,label:'Total buts',period:'90 minutes',threshold,evidence:'D0-P01',status:'EXPLORATOIRE',c3_metadata:{category}});
test('competing thresholds grouped without ranking',()=>{const x=inspect([m('M01','1,5'),m('M02','2,5')]);assert.deepEqual(x.competitors,[['M01','M02']]);assert.equal(x.entries[0].rank,null);assert.equal(x.ranking_authorized,false)});
test('missing threshold and category flagged',()=>{const x=inspect([m('M01','','NON_RENSEIGNE')]);assert.equal(x.entries[0].comparison_status,'A_COMPLETER');assert.equal(x.entries[0].missing.length,2)});
test('collective and individual remain distinguishable',()=>{const x=inspect([m('M01','2,5'),{...m('M02','1,5','INDIVIDUEL'),label:'Tirs joueur'}]);assert.equal(x.entries[0].category,'COLLECTIF');assert.equal(x.entries[1].category,'INDIVIDUEL')});
test('no automatic sports verification or selection',()=>{const x=inspect([m('M01','2,5')]);assert.equal(x.verified_sportively,false);assert.equal(x.automatic_selection,false)});
