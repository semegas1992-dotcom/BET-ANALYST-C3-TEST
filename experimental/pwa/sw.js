"use strict";
const CACHE="bet-analyst-experimental-pwa-v2";
const FILES=["index.html","viewer.js","preview-backup.js","archive-import.js","native-import.js","quarantine-import.js"];
const allowed=new Set(FILES.map(f=>new URL(f,self.registration.scope).href));
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll([...allowed]))));
self.addEventListener("fetch",e=>{if(e.request.method!=="GET"||!allowed.has(e.request.url))return;e.respondWith(caches.open(CACHE).then(async c=>await c.match(e.request)||fetch(e.request)))});
