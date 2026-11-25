const {chromium}=require("playwright");
const assert=require("node:assert/strict"),crypto=require("node:crypto"),fs=require("node:fs");
(async()=>{
const browser=await chromium.launch({headless:true});
try{
const ctx=await browser.newContext({serviceWorkers:"allow",acceptDownloads:true});
const page=await ctx.newPage();const errors=[];page.on("pageerror",e=>errors.push(e.message));
const url="http://127.0.0.1:8765/experimental/pwa/index.html";
await page.goto(url);await page.evaluate(()=>navigator.serviceWorker.ready.then(()=>true));await page.reload();await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
const keys=["BET_ANALYST_C1_HISTORY","BET_ANALYST_C3_1_DRAFT","BET_ANALYST_V1_DRAFT"];
await page.evaluate(keys=>keys.forEach(k=>localStorage.setItem(k,"sentinel:"+k)),keys);
await ctx.setOffline(true);const response=await page.reload();assert(response.fromServiceWorker());
assert.equal(await page.evaluate(()=>navigator.onLine),false);
const raw=JSON.stringify({schema:"D0_EXPERIMENTAL_V1",sport:"football",origin:"synthetic",engine_access:false,cutoff:"2026-01-02T00:00:00Z",kickoff:"2026-01-03T00:00:00Z",observations:[{id:"test",source:"synthetic_fixture",event_end:"2026-01-01T00:00:00Z",available_at:"2026-01-01T01:00:00Z",captured_at:"2026-01-01T02:00:00Z"}]});
const hash=crypto.createHash("sha256").update(raw).digest("hex");
await page.locator("#file").setInputFiles({name:"fixture.json",mimeType:"application/json",buffer:Buffer.from(raw)});
await page.locator("#hash").fill(hash);await page.locator("#read").click();await page.waitForFunction(()=>!document.querySelector("#save").disabled);
await page.locator("#save").click();await page.waitForFunction(()=>document.querySelector("#history").textContent.includes("football"));
const [download]=await Promise.all([page.waitForEvent("download"),page.locator("#export").click()]);
await download.saveAs("/tmp/preview-backup.json");const backup=fs.readFileSync("/tmp/preview-backup.json");assert.equal(JSON.parse(backup).previews.length,1);
await page.evaluate(()=>localStorage.removeItem(PreviewBackup.KEY));
await page.locator("#backup").setInputFiles({name:"backup.json",mimeType:"application/json",buffer:backup});page.once("dialog",d=>d.accept());await page.locator("#restore").click();await page.waitForFunction(()=>PreviewBackup.load(localStorage).length===1);
await page.locator("#backup").setInputFiles({name:"bad.json",mimeType:"application/json",buffer:Buffer.from('{"schema":"bad"}')});await page.locator("#restore").click();await page.waitForFunction(()=>document.querySelector("#result").textContent.includes("refusée"));
assert.equal(await page.evaluate(()=>PreviewBackup.load(localStorage).length),1);
assert(await page.evaluate(keys=>keys.every(k=>localStorage.getItem(k)==="sentinel:"+k),keys));assert.deepEqual(errors,[]);
const result={status:"PASS",browser:browser.version(),offline_reload:true,service_worker_response:true,synthetic_import:true,export_restore:true,invalid_restore_refused:true,history_keys_unchanged:keys,android:"NOT_TESTED"};fs.writeFileSync("browser-evidence.json",JSON.stringify(result,null,2));console.log(result);
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
