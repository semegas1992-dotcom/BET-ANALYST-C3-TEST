// C3.5-W — Single, manually approved collection; no schedule and no public deployment.
import {writeFile} from 'node:fs/promises';
import {createMatchSnapshot} from './c3-5-snapshot-builder.js';
const competition=process.env.COMPETITION||'PL';
const token=process.env.FOOTBALL_DATA_TOKEN;
if(process.env.PROVIDER_LICENSE_APPROVED!=='true')throw new Error('LICENSE_NOT_APPROVED');
if(!token)throw new Error('MISSING_PRIVATE_TOKEN');
if(!/^[A-Z0-9]{2,8}$/.test(competition))throw new Error('INVALID_COMPETITION');
const endpoint='https://api.football-data.org/v4/competitions/'+competition+'/matches';
const response=await fetch(endpoint,{headers:{'X-Auth-Token':token},signal:AbortSignal.timeout(7000)});
if(!response.ok)throw new Error('PROVIDER_HTTP_'+response.status);
const raw=await response.json();
const snapshot=createMatchSnapshot(raw,{competition});
await writeFile('c3-5-collected-matches.json',JSON.stringify(snapshot,null,2)+'\n',{flag:'wx',mode:0o600});
console.log('Snapshot created: competition='+competition+', count='+snapshot.matches.length+', truncated='+snapshot.truncated+', status='+snapshot.status);
