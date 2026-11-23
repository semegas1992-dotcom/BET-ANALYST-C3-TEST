const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../c3-5-preview.html'),'utf8');
test('C3.7 experimental preview never fetches provider or embeds credentials',()=>{
 assert.doesNotMatch(html,/fetch\s*\(|X-Auth-Token|FOOTBALL_DATA_TOKEN/);
 assert.match(html,/type="file"/);
});
test('C3.7 local file errors are visible and clear old match data',()=>{
 assert.match(html,/if\(file\.size>1000000\)\{currentView=null;renderMatches\(\)/);
 assert.match(html,/catch\{currentView=null;renderMatches\(\)/);
 assert.match(html,/status\.className='warning'/);
});
test('C3.7 experimental title and source transparency',()=>{
 assert.match(html,/<title>BET ANALYST — C3\.7/);
 assert.match(html,/Aucune collecte en direct/);
 assert.match(html,/non vérifié/);
});

test('C3.7 distinguishes JSON parse failure from validation processing failure',()=>{
 assert.match(html,/Fichier JSON illisible/);
 assert.match(html,/Erreur pendant la validation du fichier/);
 assert.match(html,/try\{render\(parsed\)\}/);
});
