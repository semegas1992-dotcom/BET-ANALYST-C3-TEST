'use strict';
const CACHE='bet-c3-2-candidate-v2';
const ASSETS=['./','./index.html','./c3-reader.js','./c3-metadata.js','./manifest.webmanifest','../icon-192.png','../icon-512.png'];
self.addEventListener('install',event=>{
 self.skipWaiting();
 event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)));
});
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 const names=await caches.keys();
 await Promise.all(names.filter(name=>name.startsWith('bet-c3-2-candidate-')&&name!==CACHE).map(name=>caches.delete(name)));
 await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const req=event.request;
 const url=new URL(req.url);
 const scope=new URL(self.registration.scope);
 if(req.method!=='GET'||url.origin!==scope.origin||!url.pathname.startsWith(scope.pathname))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  if(req.mode==='navigate'){
   try{
    const response=await fetch(req);
    if(response.ok)await cache.put(req,response.clone());
    return response;
   }catch(error){
    const cached=await cache.match(req)||await cache.match(new URL('./index.html',scope).href);
    if(cached)return cached;
    throw error;
   }
  }
  const cached=await cache.match(req);
  if(cached)return cached;
  const response=await fetch(req);
  if(response.ok)await cache.put(req,response.clone());
  return response;
 })());
});
