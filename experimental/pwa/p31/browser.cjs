const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch();try{
const ctx=await browser.newContext({viewport:{width:375,height:800},isMobile:true,serviceWorkers:'allow'});
const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const url='http://127.0.0.1:8765/experimental/pwa/p31/';
await page.goto(url);await page.evaluate(()=>navigator.serviceWorker.ready);await page.reload();await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
for(const offline of [false,true]){
 await ctx.setOffline(offline);await page.reload();
 for(const sport of ['football','nba','tennis']){
  await page.selectOption('#sport',sport);await page.click('#load');
  await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('Rejeu précalculé'));
  assert(await page.locator('#c4-output').textContent().then(s=>s.includes('Conclusion sportive : non établie')));
  assert.equal(await page.locator('#c4-output details h4').count(),7);
  console.log('P31_BROWSER',sport,offline?'offline':'online','PASS');
 }
}
assert.deepEqual(errors,[]);console.log('P31_BROWSER PASS; physical Android NOT_TESTED');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
