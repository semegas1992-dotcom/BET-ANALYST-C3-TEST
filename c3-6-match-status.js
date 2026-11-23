// C3.6 — Read-only classification of provider statuses; no sporting predictions.
const UPCOMING=new Set(['SCHEDULED','TIMED']);
const LIVE=new Set(['IN_PLAY','PAUSED','LIVE']);
const FINISHED=new Set(['FINISHED','AWARDED']);
const OTHER=new Set(['POSTPONED','SUSPENDED','CANCELLED']);
export function classifyMatchStatus(status){
 if(UPCOMING.has(status))return 'UPCOMING';
 if(LIVE.has(status))return 'LIVE';
 if(FINISHED.has(status))return 'FINISHED';
 if(OTHER.has(status))return 'OTHER';
 return 'UNKNOWN';
}
export function groupMatchesByStatus(matches){
 const groups={UPCOMING:[],LIVE:[],FINISHED:[],OTHER:[],UNKNOWN:[]};
 for(const match of matches){
  const category=classifyMatchStatus(match?.status);
  groups[category].push(match);
 }
 for(const list of Object.values(groups))list.sort((a,b)=>Date.parse(a.date_utc||a.utcDate)-Date.parse(b.date_utc||b.utcDate));
 return groups;
}
