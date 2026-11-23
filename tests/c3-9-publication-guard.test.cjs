const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const workflow=fs.readFileSync(path.join(__dirname,'../.github/workflows/c3-5-collect-once.yml'),'utf8');
const collector=fs.readFileSync(path.join(__dirname,'../c3-5-collect-once.mjs'),'utf8');
test('C3.9 manual-only collector cannot silently run on a schedule or push',()=>{
 assert.match(workflow,/workflow_dispatch:/);
 assert.doesNotMatch(workflow,/^\s*(schedule|push|pull_request):/m);
 assert.match(workflow,/inputs\.confirmation == 'COLLECTER'/);
 assert.match(collector,/MANUAL_CONFIRMATION_REQUIRED/);
});
test('C3.9 collected data is not deployed and artifact export is disabled until license review',()=>{
 assert.match(workflow,/PROVIDER_LICENSE_APPROVED == 'true'/);
 assert.doesNotMatch(workflow,/upload-artifact/);
 assert.match(workflow,/permissions:\s*\n\s*contents: read/);
 assert.doesNotMatch(workflow,/pages: write|deploy-pages|git push|gh-pages/);
 assert.doesNotMatch(collector,/console\.log\([^\n]*(token|raw|snapshot\.matches)/i);
});
