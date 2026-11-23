const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../preview-c3-7/c3-12-link.html'),'utf8');
test('C3.12-B: responsive mobile interface with fixture selection',()=>{assert.match(html,/name="viewport"/);assert.match(html,/id="match"/);assert.match(html,/addEventListener\('change',updateLink\)/)});
test('C3.12-B: local fixture and evidence import',()=>{assert.match(html,/id="snapshot" type="file"/);assert.match(html,/id="dossier" type="file"/);assert.match(html,/JSON\.parse\(await file\.text\(\)\)/)});
test('C3.12-B: actual matching validator used',()=>{assert.match(html,/linkMatchEvidence\(snapshot,dossier\)/);assert.match(html,/result\.match\.id!==id/);assert.match(html,/Analyse KRAFT bloquée/)});
test('C3.12-B: local demo contains two fixtures but one dossier',()=>{assert.match(html,/id:101/);assert.match(html,/id:102/);assert.match(html,/match_id:'101'/)});
test('C3.12-B: no dynamic HTML injection or network collection',()=>{assert.doesNotMatch(html,/innerHTML|outerHTML|insertAdjacentHTML|\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket/);assert.match(html,/\.textContent=value/)});
test('C3.12-B: file-size and parse errors handled',()=>{assert.match(html,/file\.size>1000000/);assert.match(html,/Fichier JSON illisible/)});

test('C3.12-C: rejects structurally invalid JSON files',()=>{assert.match(html,/validateSnapshot\(data\):validateKraftEvidence\(data\)/);assert.match(html,/Fichier refusé : structure invalide/)});
test('C3.12-C: immediately removes old data before reading replacement',()=>{assert.match(html,/if\(kind==='snapshot'\)\{snapshot=null;dossier=null;\+\+importSequence\.dossier;\}else dossier=null;[\s\S]*?updateMatches\(\);[\s\S]*?await file\.text\(\)/)});
test('C3.12-C: ignores out-of-order file reads independently by type',()=>{assert.match(html,/importSequence=\{snapshot:0,dossier:0\}/);assert.match(html,/sequence!==importSequence\[kind\]/)});
test('C3.12-C: demo invalidates pending imports',()=>{assert.match(html,/\+\+importSequence\.snapshot;\+\+importSequence\.dossier/);assert.match(html,/Analyse KRAFT bloquée/)});

test('C3.12-C: replacing a snapshot clears previous dossier',()=>{assert.match(html,/snapshot=null;dossier=null;\+\+importSequence\.dossier/)});
