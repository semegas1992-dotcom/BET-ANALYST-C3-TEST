export function reviewEvents(reports,now=Date.now()){
 if(!Array.isArray(reports)||reports.length>3)return {status:'INVALID_REPORT',events:[],engine_access:false};
 const events=[],issues=[],seen=new Set();
 for(const r of reports){
 if(!r||!['Basketball','Soccer','Tennis'].includes(r.sport)||!Array.isArray(r.events)||r.events.length>100||!String(r.source).startsWith('https://www.thesportsdb.com/api/v1/json/123/eventsday.php?')){issues.push('INVALID_SOURCE_REPORT');continue}
 if(r.status!=='QUARANTINE_UNVERIFIED'){issues.push(r.sport+': '+String(r.status));continue}
 const t=Date.parse(r.collected_at);
 for(const e of r.events){
 if(!e||typeof e.idEvent!=='string'||!e.idEvent||typeof e.strEvent!=='string'||e.strSport!==r.sport){issues.push('INVALID_EVENT');continue}
 const key=r.sport+':'+e.idEvent;if(seen.has(key)){issues.push('DUPLICATE_EVENT');continue}seen.add(key);
 const flags=[];if(!Number.isFinite(t)||t>now)flags.push('INVALID_COLLECTION_DATE');else if(now-t>86400000)flags.push('STALE_EXPERIMENTAL_24H');
 if(!/^\d{4}-\d{2}-\d{2}$/.test(e.dateEvent??''))flags.push('MISSING_EVENT_DATE');
 if(!e.strLeague)flags.push('MISSING_LEAGUE');
 const scope=r.sport==='Basketball'?(e.strLeague==='NBA'?'NBA_CANDIDATE':'OUTSIDE_NBA_OR_UNKNOWN'):'PROFESSIONAL_STATUS_UNVERIFIED';
 events.push({name:e.strEvent,league:e.strLeague||'Unknown',sport:r.sport,date:e.dateEvent,scope,flags,verified:false,collected_at:r.collected_at});
 }}
 return {status:'QUARANTINE_REVIEW',events,issues,engine_access:false,publication:'BLOCKED_RIGHTS_NOT_CONFIRMED'};
}
export function runEventReviewDemo(){const now=Date.parse('2026-11-24T12:00:00Z'),r={sport:'Basketball',source:'https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d=2026-11-24',status:'QUARANTINE_UNVERIFIED',collected_at:'2026-11-24T11:00:00Z',events:[{idEvent:'fixture',strEvent:'Fictif A - Fictif B',strSport:'Basketball',strLeague:'NBA',dateEvent:'2026-11-24'}]};const a=reviewEvents([r],now),b=reviewEvents([{...r,events:[...r.events,...r.events]}],now),d=reviewEvents([r],now+86400000);return [{id:'NBA_CANDIDATE',pass:a.events[0].scope==='NBA_CANDIDATE'},{id:'DUPLICATE',pass:b.events.length===1&&b.issues.includes('DUPLICATE_EVENT')},{id:'STALE',pass:d.events[0].flags.includes('STALE_EXPERIMENTAL_24H')},{id:'INVALID_REPORT',pass:reviewEvents(null).status==='INVALID_REPORT'},{id:'LOCK',pass:!a.engine_access&&a.publication==='BLOCKED_RIGHTS_NOT_CONFIRMED'}]}
