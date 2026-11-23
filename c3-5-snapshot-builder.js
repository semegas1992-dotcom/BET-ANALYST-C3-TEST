// C3.5-T — Convert an approved provider response to a static read-only snapshot.
// This module does not fetch data, schedule jobs, or publish anything.
export function createMatchSnapshot(raw,{competition,retrievedAt=new Date().toISOString()}={}){
 if(typeof competition!=='string'||!/^[A-Z0-9]{2,8}$/.test(competition))throw new Error('INVALID_COMPETITION');
 if(!raw||!Array.isArray(raw.matches))throw new Error('INVALID_PROVIDER_RESPONSE');
 if(!Number.isFinite(Date.parse(retrievedAt)))throw new Error('INVALID_RETRIEVAL_DATE');
 // Keep the next scheduled fixtures first when the provider returns more than 100.
 // Preserve the provider's data without fabricating missing matches.
 const referenceTime=Date.parse(retrievedAt);
 const rank=m=>{
  const time=Date.parse(m?.utcDate);
  if((m?.status==='SCHEDULED'||m?.status==='TIMED')&&Number.isFinite(time)&&time>=referenceTime)return 0;
  if(m?.status==='IN_PLAY'||m?.status==='PAUSED'||m?.status==='LIVE')return 1;
  if(m?.status==='SCHEDULED'||m?.status==='TIMED')return 2;
  return 3;
 };
 const selected=[...raw.matches].sort((a,b)=>rank(a)-rank(b)||((Date.parse(a?.utcDate)||0)-(Date.parse(b?.utcDate)||0))).slice(0,100);
 if(selected.some(m=>!Number.isSafeInteger(m?.id)||m.id<=0||typeof m.utcDate!=='string'||!Number.isFinite(Date.parse(m.utcDate))||typeof m.homeTeam?.name!=='string'||!m.homeTeam.name.trim()||typeof m.awayTeam?.name!=='string'||!m.awayTeam.name.trim()))throw new Error('INCOMPLETE_MATCH_DATA');
 const matches=selected.map(m=>({
  id:Number.isSafeInteger(m?.id)?m.id:null,
  utcDate:typeof m?.utcDate==='string'?m.utcDate:null,
  status:typeof m?.status==='string'?m.status:null,
  homeTeam:typeof m?.homeTeam?.name==='string'?m.homeTeam.name:null,
  awayTeam:typeof m?.awayTeam?.name==='string'?m.awayTeam.name:null
 }));
 return {
  schema:'BET_ANALYST_MATCH_SNAPSHOT_V1',
  status:'RECEIVED_UNVERIFIED',
  provider:'football-data.org',
  source_endpoint:'https://api.football-data.org/v4/competitions/'+competition+'/matches',
  competition,
  retrieved_at:retrievedAt,
  coverage:'BASIC_MATCHES_ONLY',
  truncated:raw.matches.length>100,
  matches
 };
}
