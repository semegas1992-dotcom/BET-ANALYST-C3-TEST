'use strict';
/* C3.3-B: contrôles documentaires, jamais une validation sportive automatique. */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.C33Coherence=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const KEYS=['A','B','C'];
 function inspect(input){
  if(!input||typeof input!=='object'||Array.isArray(input)||KEYS.some(k=>typeof input[k]!=='string'))
   throw Error('Scénarios A/B/C non conformes');
  const normalized=Object.fromEntries(KEYS.map(k=>[k,input[k].trim().replace(/\s+/g,' ')]));
  const missing=KEYS.filter(k=>!normalized[k]);
  const identical=[];
  for(let i=0;i<KEYS.length;i++)for(let j=i+1;j<KEYS.length;j++){
   const a=KEYS[i],b=KEYS[j];
   if(normalized[a]&&normalized[a].toLocaleLowerCase('fr')===normalized[b].toLocaleLowerCase('fr'))identical.push([a,b]);
  }
  const warnings=[];
  if(missing.length)warnings.push('Scénarios non renseignés : '+missing.join(', ')+'.');
  if(identical.length)warnings.push('Textes identiques à examiner : '+identical.map(pair=>pair.join('/')).join(', ')+'.');
  if(!missing.length&&!identical.length)warnings.push('Contradictions, probabilités, hypothèses et incertitudes : examen humain nécessaire.');
  return {status:missing.length?'INCOMPLET':identical.length?'A_EXAMINER':'REVUE_HUMAINE_REQUISE',missing,identical,warnings,validated_sportively:false,probabilities_calculated:false,contradictions_verified:false};
 }
 return Object.freeze({inspect});
});
