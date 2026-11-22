'use strict';
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.C35Ingestion=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const SPORTS=['FOOTBALL','TENNIS','NBA'];
 const STATES=['VERIFIED','DECLARED','MISSING','CONFLICT','STALE'];
 function nonempty(x){return typeof x==='string'&&x.trim().length>0}
 function normalize(input){
  if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Dossier invalide');
  if(!SPORTS.includes(input.sport))throw Error('Sport non pris en charge');
  if(!nonempty(input.event))throw Error('Rencontre manquante');
  if(!Array.isArray(input.facts))throw Error('Liste des faits manquante');
  const facts=input.facts.map((f,i)=>{
   if(!f||typeof f!=='object'||Array.isArray(f)||!nonempty(f.key))throw Error('Fait invalide '+i);
   const state=STATES.includes(f.state)?f.state:'MISSING';
   const source=f.source&&typeof f.source==='object'?f.source:{};
   const citation=nonempty(source.reference)?source.reference.trim():null;
   const observedAt=nonempty(source.observed_at)?source.observed_at.trim():null;
   const sourceUrl=nonempty(source.url)?source.url.trim():null;
   if(sourceUrl&&!/^https:\/\//i.test(sourceUrl))throw Error('URL de source non HTTPS');
   const value=(typeof f.value==='string'||typeof f.value==='number')?f.value:null;
   const hasTrace=!!(citation&&observedAt);
   const effectiveState=state==='VERIFIED'&&(!hasTrace||value===null)?'DECLARED':state;
   return {key:f.key.trim(),value,state:effectiveState,source:{reference:citation,url:sourceUrl,observed_at:observedAt},warnings:[...(state==='VERIFIED'&&effectiveState!=='VERIFIED'?['VERIFICATION_NON_JUSTIFIEE']:[]),...(!hasTrace?['TRACABILITE_INCOMPLETE']:[])]};
  });
  const duplicateKeys=facts.map(x=>x.key).filter((k,i,a)=>a.indexOf(k)!==i);
  return {schema:'BET_ANALYST_C3_5_INGESTION_V1',sport:input.sport,event:input.event.trim(),facts,duplicate_keys:[...new Set(duplicateKeys)],automatic_fetch:false,sporting_validation:false,probabilities_computed:false,ready_for_sporting_analysis:false};
 }
 return Object.freeze({normalize,SPORTS:Object.freeze(SPORTS.slice())});
});