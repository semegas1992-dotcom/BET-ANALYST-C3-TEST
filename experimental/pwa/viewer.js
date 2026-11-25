"use strict";
let current=null;
document.getElementById("read").addEventListener("click",async()=>{
 const out=document.getElementById("result");out.textContent="";current=null;document.getElementById("save").disabled=true;
 try{const f=document.getElementById("file").files[0];if(!f||f.size>1048576)throw Error("Fichier absent ou trop volumineux");
 const expected=document.getElementById("hash").value.trim()||undefined;
 const bytes=await f.arrayBuffer();const text=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(bytes);
 const r=await ArchiveImport.inspectArchive(text,expected);
 current=r;document.getElementById("save").disabled=false;out.textContent=JSON.stringify(r,null,2);
 }catch(e){out.textContent="Import refusé : "+e.message}
});

const el=id=>document.getElementById(id);
function refresh(){try{el("history").textContent=JSON.stringify(PreviewBackup.load(localStorage),null,2)}catch(e){el("history").textContent="Stockage indisponible : "+e.message}}
function action(fn){return async()=>{try{await fn();refresh()}catch(e){el("result").textContent="Opération refusée : "+e.message}}}
el("save").onclick=action(()=>{if(!current)throw Error("Aucun aperçu");const old=PreviewBackup.load(localStorage);PreviewBackup.restore(localStorage,PreviewBackup.encode([...old.filter(p=>p.file_sha256!==current.file_sha256),current]))});
el("export").onclick=action(()=>{const url=URL.createObjectURL(new Blob([PreviewBackup.encode(PreviewBackup.load(localStorage))],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="bet-analyst-quarantine-backup.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
el("restore").onclick=action(async()=>{const f=el("backup").files[0];if(!f||f.size>131072)throw Error("Fichier invalide");const text=new TextDecoder("utf-8",{fatal:true}).decode(await f.arrayBuffer());PreviewBackup.decode(text);if(confirm("Remplacer uniquement les aperçus expérimentaux ? Provenance non authentifiée."))PreviewBackup.restore(localStorage,text)});
refresh();
if("serviceWorker" in navigator){
 const sw=navigator.serviceWorker, expected=new URL("sw.js",location.href).href;
 const controlled=()=>sw.controller?.scriptURL===expected && sw.controller.state==="activated";
 const status=()=>{el("offline").textContent=controlled()?"Service worker actif ; cache prêt pour essai hors ligne.":"Cache en attente de contrôle."};
 sw.addEventListener("controllerchange",status);status();
 if(!controlled())sw.register("./sw.js",{scope:"./",updateViaCache:"none"}).then(()=>sw.ready).then(status).catch(e=>{if(controlled())status();else el("offline").textContent="Cache indisponible : "+e.message});
}

el("demo").onclick=action(async()=>{current=null;el("save").disabled=true;const raw="{\"schema\":\"D0_EXPERIMENTAL_V1\",\"sport\":\"football\",\"origin\":\"synthetic\",\"engine_access\":false,\"cutoff\":\"2026-01-02T00:00:00Z\",\"kickoff\":\"2026-01-03T00:00:00Z\",\"observations\":[{\"id\":\"android-demo-1\",\"source\":\"synthetic_fixture\",\"event_end\":\"2026-01-01T00:00:00Z\",\"available_at\":\"2026-01-01T01:00:00Z\",\"captured_at\":\"2026-01-01T02:00:00Z\"}]}";const expected=await NativeImport.hash(raw);current=await ArchiveImport.inspectArchive(raw,expected);el("result").textContent=JSON.stringify(current,null,2);el("save").disabled=false});
