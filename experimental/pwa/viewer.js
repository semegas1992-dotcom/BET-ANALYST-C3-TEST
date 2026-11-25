"use strict";
document.getElementById("read").addEventListener("click",async()=>{
 const out=document.getElementById("result");out.textContent="";
 try{const f=document.getElementById("file").files[0];if(!f||f.size>1048576)throw Error("Fichier absent ou trop volumineux");
 const expected=document.getElementById("hash").value.trim()||undefined;
 const bytes=await f.arrayBuffer();const text=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(bytes);
 const r=await ArchiveImport.inspectArchive(text,expected);
 out.textContent=JSON.stringify(r,null,2);
 }catch(e){out.textContent="Import refusé : "+e.message}
});
