'use strict';
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.C34Markets=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
 function inspect(markets){
  if(!Array.isArray(markets))throw Error('Liste de marchés invalide');
  const groups=new Map();
  const entries=markets.map(m=>{
   if(!m||typeof m!=='object'||typeof m.id!=='string'||typeof m.label!=='string'||typeof m.period!=='string'||typeof m.threshold!=='string'||typeof m.evidence!=='string')throw Error('Marché invalide');
   const category=m.c3_metadata&&m.c3_metadata.category||'NON_RENSEIGNE';
   const missing=[];
   if(!m.threshold.trim())missing.push('seuil non renseigné');
   if(!m.evidence.trim())missing.push('preuves non renseignées');
   if(category==='NON_RENSEIGNE')missing.push('catégorie non renseignée');
   const key=[m.label.trim().toLocaleLowerCase('fr'),m.period.trim().toLocaleLowerCase('fr')].join('|');
   if(!groups.has(key))groups.set(key,[]);
   groups.get(key).push(m.id);
   return {id:m.id,label:m.label,period:m.period,threshold:m.threshold,category,declared_status:m.status,missing,comparison_status:missing.length?'A_COMPLETER':'REVUE_HUMAINE',rank:null,probability:null,verified:false};
  });
  const competitors=[...groups.values()].filter(g=>g.length>1);
  return {entries,competitors,ranking_authorized:false,verified_sportively:false,automatic_selection:false};
 }
 return Object.freeze({inspect});
});