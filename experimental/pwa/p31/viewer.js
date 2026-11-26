'use strict';
const status=document.getElementById('status'),out=document.getElementById('c4-output');
document.getElementById('load').onclick=async()=>{
 out.replaceChildren();
 try{
 const response=await fetch('./reports.json');if(!response.ok)throw Error('Rapports indisponibles');
 const data=await response.json(),v=data[document.getElementById('sport').value];
 if(!v||v.scope!=='PRECOMPUTED_SYNTHETIC'||v.registered_result.engine_access!==false||v.registered_result.qualification!=='BLOCKED'||v.registered_result.publication!=='BLOCKED')throw Error('Verrous absents');
 // Reuse existing reader via its browser export.
 window.P31Reader.render(v.report,out,document);
 status.textContent='Rejeu précalculé — contrôle Python enregistré : '+v.registered_result.state+' ; aucune conclusion sportive.';
 }catch(e){out.replaceChildren();status.textContent='Refus : '+e.message}
};
if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(e=>{status.textContent='Cache indisponible : '+e.message});
