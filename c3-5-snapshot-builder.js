// C3.5-T — Convert an approved provider response to a static read-only snapshot.
// This module does not fetch data, schedule jobs, or publish anything.
export function createMatchSnapshot(raw,{competition,retrievedAt=new Date().toISOString()}={}){
 if(typeof competition!=='string'||!/^[A-Z0-9]{2,8}$/.test(competition))throw new Error('INVALID_COMPETITION');
 if(!raw||!Array.isArray(raw.matches))throw new Error('INVALID_PROVIDER_RESPONSE');
 if(!Number.isFinite(Date.parse(retrievedAt)))throw new Error('INVALID_RETRIEVAL_DATE');
 const selected=raw.matches.slice(0,100);
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
