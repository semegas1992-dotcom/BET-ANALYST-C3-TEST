import {createMatchSnapshot} from './c3-5-snapshot-builder.js';
export function openLigaSnapshot(rows,receipt){
 if(receipt.engine_access!==false||receipt.publication!=='BLOCKED'||receipt.qualification!=='BLOCKED'||receipt.source!=='OpenLigaDB')throw Error('QUARANTINE_REQUIRED');
 const cutoff=Date.parse(receipt.cutoff), captured=Date.parse(receipt.captured_at);
 if(!Number.isFinite(cutoff)||!Number.isFinite(captured)||captured>cutoff)throw Error('CUTOFF');
 const matches=rows.filter(m=>m.matchIsFinished===false&&Date.parse(m.matchDateTimeUTC)>cutoff).map(m=>({id:m.matchID,utcDate:m.matchDateTimeUTC,status:'SCHEDULED',homeTeam:{name:m.team1?.teamName},awayTeam:{name:m.team2?.teamName}}));
 const snapshot=createMatchSnapshot({matches},{competition:'BL1',retrievedAt:receipt.captured_at});
 return {...snapshot,provider:'OpenLigaDB',source_endpoint:'https://api.openligadb.de/getmatchdata/bl1/',source_sha256:receipt.sha256,cutoff:receipt.cutoff,engine_access:false,publication:'BLOCKED',qualification:'BLOCKED',status:'QUARANTINE_UNVERIFIED'};
}
