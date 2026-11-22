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
