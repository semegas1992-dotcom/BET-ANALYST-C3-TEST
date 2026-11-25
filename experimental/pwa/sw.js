"use strict";
const CACHE="bet-analyst-experimental-pwa-v3";
const scope=self.registration.scope;
const shell=new URL("./",scope).href;
const index=new URL("index.html",scope).href;
const assets=["viewer.js","preview-backup.js","archive-import.js","native-import.js","quarantine-import.js"].map(f=>new URL(f,scope).href);
self.addEventListener("install",e=>e.waitUntil((async()=>{const c=await caches.open(CACHE);await c.addAll([shell,...assets]);await self.skipWaiting()})()));
self.addEventListener("activate",e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith("bet-analyst-experimental-pwa-")&&k!==CACHE)await caches.delete(k);await self.clients.claim()})()));
self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;const u=e.request.url;const key=(u===shell||u===index)?shell:assets.includes(u)?u:null;if(!key)return;e.respondWith((async()=>{const c=await caches.open(CACHE);return await c.match(key)||fetch(e.request)})())});
