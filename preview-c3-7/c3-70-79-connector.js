// Experimental public NBA scoreboard endpoint; availability and CORS not established.
export const endpoint='https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json';
export function normalizeScoreboard(payload,collectedAt){
 const s=payload?.scoreboard;
 if(!s||!/^\d{4}-\d{2}-\d{2}$/.test(s.gameDate??'')||!Array.isArray(s.games)||s.games.length>100)return {status:'INVALID_PAYLOAD',games:[],engine_access:false};
 const games=[],issues=[];
 for(const g of s.games){
 if(!g||typeof g.gameId!=='string'||!g.gameId||typeof g.homeTeam?.teamName!=='string'||typeof g.awayTeam?.teamName!=='string'||![1,2,3].includes(g.gameStatus)){issues.push('INVALID_GAME');continue}
 games.push({id:g.gameId,date:s.gameDate,home:g.homeTeam.teamName,away:g.awayTeam.teamName,status:g.gameStatus,reference:endpoint,collected_at:collectedAt,verified:false});
 }
 return {status:issues.length?'QUARANTINE_REVIEW':'QUARANTINE_UNVERIFIED',games,issues,engine_access:false,verification:'NOT_PERFORMED'};
}
export async function collectScoreboard(fetcher=fetch){
 try{const r=await fetcher(endpoint,{credentials:'omit',cache:'no-store',signal:AbortSignal.timeout(12000)});if(!r.ok)return {status:'HTTP_ERROR',http_status:r.status,games:[],engine_access:false};return normalizeScoreboard(await r.json(),new Date().toISOString())}catch{return {status:'NETWORK_OR_CORS_OR_PARSE_ERROR',games:[],engine_access:false}}
}
export async function runConnectorDemo(){
 const fixture={scoreboard:{gameDate:'2026-11-24',games:[{gameId:'SIM',gameStatus:1,homeTeam:{teamName:'Fictif A'},awayTeam:{teamName:'Fictif B'}}]}};
 const ok=await collectScoreboard(async()=>({ok:true,json:async()=>fixture}));
 const bad=normalizeScoreboard({},null);
 const http=await collectScoreboard(async()=>({ok:false,status:403}));
 const net=await collectScoreboard(async()=>{throw Error('fixture')});
 return [{id:'NORMALIZATION',pass:ok.games.length===1&&ok.status==='QUARANTINE_UNVERIFIED'},{id:'INVALID_PAYLOAD',pass:bad.status==='INVALID_PAYLOAD'},{id:'HTTP_ERROR',pass:http.status==='HTTP_ERROR'},{id:'NETWORK_ERROR',pass:net.status==='NETWORK_OR_CORS_OR_PARSE_ERROR'},{id:'ENGINE_LOCK',pass:[ok,bad,http,net].every(x=>!x.engine_access)}];
}
