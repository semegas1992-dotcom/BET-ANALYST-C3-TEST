'use strict';
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.C35Provider=factory()})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const SPORTS=['FOOTBALL','TENNIS','NBA'];
 function assertProvider(p){
  if(!p||typeof p!=='object'||!p.id||typeof p.id!=='string'||!Array.isArray(p.sports)||!p.sports.length||p.sports.some(s=>!SPORTS.includes(s))||typeof p.fetchMatch!=='function')throw Error('Connecteur invalide');
  if(p.authorization_confirmed!==true)throw Error('Autorisation du fournisseur non confirmée');
  return p;
 }
 async function collect(provider,query,options={}){
  assertProvider(provider);
  if(!query||!SPORTS.includes(query.sport)||typeof query.event!=='string'||!query.event.trim())throw Error('Recherche de rencontre invalide');
  if(!provider.sports.includes(query.sport))return {status:'UNSUPPORTED',provider:provider.id,match:null};
  const timeout=Number.isInteger(options.timeout_ms)&&options.timeout_ms>0?options.timeout_ms:8000;
  const AbortControllerClass=typeof AbortController==='function'?AbortController:null;
  const controller=AbortControllerClass?new AbortControllerClass():null;
  let timer;
  try{
   const response=await Promise.race([
    Promise.resolve().then(()=>provider.fetchMatch({...query},controller?{signal:controller.signal}:{})),
    new Promise((_,reject)=>{timer=setTimeout(()=>{if(controller)controller.abort();reject(Error('TIMEOUT'))},timeout)})
   ]);
   if(!response||typeof response!=='object'||!Array.isArray(response.facts))throw Error('FORMAT_INVALID');
   return {status:'RECEIVED_UNVERIFIED',provider:provider.id,match:{sport:query.sport,event:query.event,facts:response.facts},retrieved_at:new Date().toISOString()};
  }catch(err){
   const message=err&&err.message||'UNKNOWN';
   return {status:'ERROR',provider:provider.id,error:message==='TIMEOUT'?'TIMEOUT':'PROVIDER_ERROR',match:null};
  }finally{if(timer)clearTimeout(timer)}
 }
 return Object.freeze({assertProvider,collect});
});