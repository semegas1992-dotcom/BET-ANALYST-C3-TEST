// C3.5-W — Single, manually approved collection; no schedule and no public deployment.
import {writeFile} from 'node:fs/promises';
import {createMatchSnapshot} from './c3-5-snapshot-builder.js';
const competition=process.env.COMPETITION||'PL';
const token=process.env.FOOTBALL_DATA_TOKEN;
if(process.env.COLLECTION_CONFIRMATION!=='COLLECTER')throw new Error('MANUAL_CONFIRMATION_REQUIRED');
if(!token)throw new Error('MISSING_PRIVATE_TOKEN');
if(!/^[A-Z0-9]{2,8}$/.test(competition))throw new Error('INVALID_COMPETITION');
const endpoint='https://api.football-data.org/v4/competitions/'+competition+'/matches';
const response=await fetch(endpoint,{headers:{'X-Auth-Token':token},signal:AbortSignal.timeout(7000)});
if(!response.ok)throw new Error('PROVIDER_HTTP_'+response.status);
const raw=await response.json();
const snapshot=createMatchSnapshot(raw,{competition});
await writeFile('c3-5-collected-matches.json',JSON.stringify(snapshot,null,2)+'\n',{flag:'wx',mode:0o600});
const statuses={upcoming:0,live:0,finished:0,other:0,unknown:0};
for(const m of snapshot.matches){
 if(['SCHEDULED','TIMED'].includes(m.status))statuses.upcoming++;
 else if(['IN_PLAY','PAUSED','LIVE'].includes(m.status))statuses.live++;
 else if(['FINISHED','AWARDED'].includes(m.status))statuses.finished++;
 else if(['POSTPONED','SUSPENDED','CANCELLED'].includes(m.status))statuses.other++;
 else statuses.unknown++;
}
console.log('Snapshot created: competition='+competition+', count='+snapshot.matches.length+', truncated='+snapshot.truncated+', status='+snapshot.status);
console.log('Snapshot summary (unverified): '+JSON.stringify(statuses));
