const {inspectArchive}=require("./archive-import.js");
const fs=require("node:fs");
(async()=>{const raw=fs.readFileSync(0);const text=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(raw);const p=await inspectArchive(text,process.argv[2]);console.log(JSON.stringify(p));})().catch(e=>{console.error(e);process.exitCode=1});
