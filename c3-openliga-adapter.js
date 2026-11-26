import {createMatchSnapshot} from './c3-5-snapshot-builder.js';
export async function openLigaSnapshot(raw,receipt){
 if(!(raw instanceof Uint8Array))throw Error('ORIGINAL_BYTES_REQUIRED');
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
 if(hash!==receipt.sha256)throw Error('SOURCE_HASH_MISMATCH');
 const rows=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
 if(!Array.isArray(rows))throw Error('INVALID_SOURCE');
 if(receipt.engine_access!==false||receipt.publication!=='BLOCKED'||receipt.qualification!=='BLOCKED'||receipt.source!=='OpenLigaDB')throw Error('QUARANTINE_REQUIRED');
 const cutoff=Date.parse(receipt.cutoff), captured=Date.parse(receipt.captured_at);
 if(!Number.isFinite(cutoff)||!Number.isFinite(captured)||captured>cutoff)throw Error('CUTOFF');
 const matches=rows.filter(m=>m.matchIsFinished===false&&Date.parse(m.matchDateTimeUTC)>cutoff).map(m=>({id:m.matchID,utcDate:m.matchDateTimeUTC,status:'SCHEDULED',homeTeam:{name:m.team1?.teamName},awayTeam:{name:m.team2?.teamName}}));
 const snapshot=createMatchSnapshot({matches},{competition:'BL1',retrievedAt:receipt.captured_at});
 return {...snapshot,provider:'OpenLigaDB',source_endpoint:'https://api.openligadb.de/getmatchdata/bl1/',source_sha256:receipt.sha256,cutoff:receipt.cutoff,engine_access:false,publication:'BLOCKED',qualification:'BLOCKED',status:'QUARANTINE_UNVERIFIED'};
}
