// C3.5-M: read-only snapshot validator. No provider calls, secrets or automatic deployment.
const MAX_AGE_MS=15*60*1000;
export function validateSnapshot(input,{now=Date.now(),maxAgeMs=MAX_AGE_MS}={}){
 const errors=[];
 if(!input||typeof input!=='object'||Array.isArray(input))return {usable:false,freshness:'INVALID',errors:['INVALID_OBJECT'],matches:[]};
 if(input.schema!==undefined&&input.schema!=='BET_ANALYST_MATCH_SNAPSHOT_V1')errors.push('INVALID_SCHEMA');
 if(input.status!=='RECEIVED_UNVERIFIED')errors.push('INVALID_STATUS');
 if(input.provider!=='football-data.org')errors.push('UNKNOWN_PROVIDER');
 if(typeof input.source_endpoint!=='string'||!/^https:\/\/api\.football-data\.org\/v4\/competitions\/[A-Z0-9]{2,8}\/matches$/.test(input.source_endpoint))errors.push('INVALID_SOURCE');
 if(typeof input.competition!=='string'||!/^[A-Z0-9]{2,8}$/.test(input.competition))errors.push('INVALID_COMPETITION');
 if(typeof input.source_endpoint==='string'&&typeof input.competition==='string'&&!input.source_endpoint.endsWith('/'+input.competition+'/matches'))errors.push('SOURCE_COMPETITION_MISMATCH');
 if(input.coverage!=='BASIC_MATCHES_ONLY')errors.push('INVALID_COVERAGE');
 if(typeof input.truncated!=='boolean')errors.push('MISSING_TRUNCATION_FLAG');
 if(!Array.isArray(input.matches)||input.matches.length>100)errors.push('INVALID_MATCHES');
 else if(input.matches.some(m=>!m||typeof m!=='object'||Array.isArray(m)||!Number.isSafeInteger(m.id)||m.id<=0||typeof m.utcDate!=='string'||!Number.isFinite(Date.parse(m.utcDate))||typeof m.homeTeam!=='string'||!m.homeTeam.trim()||typeof m.awayTeam!=='string'||!m.awayTeam.trim()))errors.push('INVALID_MATCH_FIELDS');
 if(Array.isArray(input.matches)&&new Set(input.matches.map(m=>m?.id)).size!==input.matches.length)errors.push('DUPLICATE_MATCH_IDS');
 const retrieved=typeof input.retrieved_at==='string'?Date.parse(input.retrieved_at):NaN;
 if(!Number.isFinite(retrieved))errors.push('INVALID_TIMESTAMP');
 const age=now-retrieved;
 const freshness=!Number.isFinite(retrieved)?'INVALID':age<0?'FUTURE':age>maxAgeMs?'STALE':'FRESH';
 if(freshness==='FUTURE')errors.push('FUTURE_TIMESTAMP');
 if(!Number.isFinite(maxAgeMs)||maxAgeMs<0)errors.push('INVALID_MAX_AGE');
 const usable=errors.length===0;
 return {usable,freshness,errors,matches:usable?input.matches:[],retrieved_at:input.retrieved_at??null,competition:input.competition??null,truncated:input.truncated===true,verified:false};
}
