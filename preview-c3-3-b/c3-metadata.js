'use strict';
/* C3.2 candidate: lossless optional metadata handling, no automatic verification. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.C3Metadata=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const categories=['COLLECTIF','INDIVIDUEL','NON_RENSEIGNE'];
 const reviews=['A_VERIFIER','DOCUMENTE','INCOMPLET'];
 const statuses=['SOUTENU SPORTIVEMENT','CONDITIONNEL','EXPLORATOIRE','NON RETENU'];
 const required=['id','label','period','threshold','evidence','status'];
 function isObject(x){return x!==null&&typeof x==='object'&&!Array.isArray(x)}
 function validateMarket(m){
  if(!isObject(m)||required.some(k=>typeof m[k]!=='string'))throw Error('Marché invalide');
  if(!m.id.trim()||!m.label.trim()||!m.period.trim()||!m.evidence.trim()||!statuses.includes(m.status))throw Error('Marché incomplet');
  if(Object.prototype.hasOwnProperty.call(m,'c3_metadata')){
   const x=m.c3_metadata;
   if(!isObject(x)||!categories.includes(x.category)||!reviews.includes(x.review_status)||['verified_evidence','hypotheses','missing_information'].some(k=>!Array.isArray(x[k])||x[k].some(v=>typeof v!=='string')))throw Error('Métadonnées C3.2 invalides');
  }
  return true;
 }
 function cloneMarket(m){validateMarket(m);return JSON.parse(JSON.stringify(m))}
 function metadata(m){validateMarket(m);return Object.prototype.hasOwnProperty.call(m,'c3_metadata')?JSON.parse(JSON.stringify(m.c3_metadata)):{category:'NON_RENSEIGNE',verified_evidence:[],hypotheses:[],missing_information:[],review_status:'A_VERIFIER'}}
 function cloneMarkets(ms){if(!Array.isArray(ms)||ms.length>100)throw Error('Liste de marchés invalide');const ids=new Set();return ms.map(m=>{const x=cloneMarket(m);if(ids.has(x.id))throw Error('Identifiant de marché dupliqué');ids.add(x.id);return x})}
 return Object.freeze({validateMarket,cloneMarket,cloneMarkets,metadata});
});
