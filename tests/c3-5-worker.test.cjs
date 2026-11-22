'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const workerPromise=import('../backend/c3-5-worker.mjs').then(m=>m.default);
const url='https://worker.example/v1/football/matches?competition=PL';
async function run(path=url,env={},options={}){const worker=await workerPromise;const request=new Request(path,{method:options.method||'GET',headers:options.origin?{Origin:options.origin}:{}});const response=await worker.fetch(request,env);return {code:response.status,body:response.status===204?null:await response.json(),headers:response.headers}}
test('health never claims provider connected',async()=>{const r=await run('https://worker.example/health');assert.equal(r.code,200);assert.equal(r.body.provider_connected,false)});
test('missing secret blocks real provider calls',async()=>{const r=await run();assert.equal(r.code,503);assert.equal(r.body.status,'NOT_CONFIGURED')});
test('disabled provider blocks requests',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy'});assert.equal(r.code,503);assert.equal(r.body.status,'PROVIDER_DISABLED')});
test('unapproved browser origin rejected',async()=>{const r=await run(url,{ALLOWED_ORIGIN:'https://app.example'},{origin:'https://evil.example'});assert.equal(r.code,403);assert.equal(r.body.status,'FORBIDDEN_ORIGIN')});
test('allowed browser preflight does not fetch provider',async()=>{const r=await run(url,{ALLOWED_ORIGIN:'https://app.example'},{method:'OPTIONS',origin:'https://app.example'});assert.equal(r.code,204);assert.equal(r.headers.get('access-control-allow-origin'),'https://app.example')});
test('unsupported HTTP method rejected',async()=>{const r=await run(url,{}, {method:'POST'});assert.equal(r.code,405)});
test('unknown route rejected',async()=>{const r=await run('https://worker.example/other');assert.equal(r.code,404)});
test('competition allowlist blocks unapproved competition',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'BL1'});assert.equal(r.code,403)});
test('malformed competition rejected',async()=>{const r=await run('https://worker.example/v1/football/matches?competition=../../secret',{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true'});assert.equal(r.code,400)});

test('no limiter binding fails closed before external provider call',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL'});assert.equal(r.code,503);assert.equal(r.body.status,'RATE_LIMIT_NOT_CONFIGURED')});
test('exhausted provider quota returns 429',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:{get:async()=>null,put:async()=>{}},RATE_LIMITER:{limit:async()=>({success:false})}});assert.equal(r.code,429);assert.equal(r.body.status,'RATE_LIMITED')});
test('limiter failure fails closed',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:{get:async()=>null,put:async()=>{}},RATE_LIMITER:{limit:async()=>{throw Error('unavailable')}}});assert.equal(r.code,503);assert.equal(r.body.status,'RATE_LIMIT_UNAVAILABLE')});

test('missing cache fails closed before provider call',async()=>{const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',RATE_LIMITER:{limit:async()=>({success:true})}});assert.equal(r.code,503);assert.equal(r.body.status,'CACHE_NOT_CONFIGURED')});
test('fresh cached response skips limiter and provider',async()=>{let limits=0;const cache={get:async()=>({status:'RECEIVED_UNVERIFIED',competition:'PL',retrieved_at:new Date().toISOString(),matches:[]}),put:async()=>{throw Error('unexpected write')}};const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:cache,RATE_LIMITER:{limit:async()=>{limits++;return {success:true}}}});assert.equal(r.code,200);assert.equal(r.body.cache,'HIT');assert.equal(limits,0)});
test('cache read failure fails closed',async()=>{const cache={get:async()=>{throw Error('down')},put:async()=>{}};const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:cache,RATE_LIMITER:{limit:async()=>({success:true})}});assert.equal(r.code,503);assert.equal(r.body.status,'CACHE_UNAVAILABLE')});

test('cache miss calls mocked provider and writes cache, without real network',async()=>{
 const original=globalThis.fetch;let calls=0,writes=0,limits=0;
 globalThis.fetch=async (target,options)=>{calls++;assert.equal(target,'https://api.football-data.org/v4/competitions/PL/matches');assert.equal(options.headers['X-Auth-Token'],'dummy');return new Response(JSON.stringify({matches:[{id:123,utcDate:'2026-11-23T20:00:00Z',status:'SCHEDULED',homeTeam:{name:'A'},awayTeam:{name:'B'}}]}),{status:200,headers:{'content-type':'application/json'}})};
 try{
  const cache={get:async()=>null,put:async(key,payload,opts)=>{writes++;assert.equal(key,'football-data:matches:PL');assert.equal(opts.expirationTtl,300);assert.equal(JSON.parse(payload).matches.length,1)}};
  const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:cache,RATE_LIMITER:{limit:async({key})=>{limits++;assert.equal(key,'football-data:global');return {success:true}}}});
  assert.equal(r.code,200);assert.equal(r.body.status,'RECEIVED_UNVERIFIED');assert.equal(r.body.cache,'MISS');assert.equal(r.body.matches[0].homeTeam,'A');assert.equal(calls,1);assert.equal(writes,1);assert.equal(limits,1);
 }finally{globalThis.fetch=original}
});
test('provider error does not expose secret',async()=>{
 const original=globalThis.fetch;globalThis.fetch=async()=>new Response('failure',{status:429});
 try{const r=await run(url,{FOOTBALL_DATA_TOKEN:'secret-not-to-leak',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:{get:async()=>null,put:async()=>{}},RATE_LIMITER:{limit:async()=>({success:true})}});assert.equal(r.code,502);assert.equal(r.body.http_status,429);assert.ok(!JSON.stringify(r.body).includes('secret-not-to-leak'))}
 finally{globalThis.fetch=original}
});

test('stale cache is never served as fresh when quota is exhausted',async()=>{
 const stale=new Date(Date.now()-600000).toISOString();
 const cache={get:async()=>({status:'RECEIVED_UNVERIFIED',competition:'PL',retrieved_at:stale,matches:[{id:1}]}),put:async()=>{}};
 const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:cache,RATE_LIMITER:{limit:async()=>({success:false})}});
 assert.equal(r.code,429);assert.equal(r.body.status,'RATE_LIMITED');
});
test('malformed cache entry is never treated as verified',async()=>{
 const cache={get:async()=>({status:'VERIFIED',competition:'PL',retrieved_at:new Date().toISOString(),matches:[{id:1}]}),put:async()=>{}};
 const r=await run(url,{FOOTBALL_DATA_TOKEN:'dummy',PROVIDER_ENABLED:'true',ALLOWED_COMPETITIONS:'PL',MATCH_CACHE:cache,RATE_LIMITER:{limit:async()=>({success:false})}});
 assert.equal(r.code,429);
});
