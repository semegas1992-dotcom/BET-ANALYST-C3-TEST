// C3.50–59: candidate public source directory and isolated intake.
export const sources=Object.freeze([
 {id:'FIFA',sport:'FOOTBALL',url:'https://www.fifa.com/',type:'GOVERNING_BODY',domains:['competition']},
 {id:'UEFA',sport:'FOOTBALL',url:'https://www.uefa.com/',type:'GOVERNING_BODY',domains:['schedule','results','statistics']},
 {id:'LFP',sport:'FOOTBALL',url:'https://www.ligue1.com/',type:'COMPETITION',domains:['schedule','results','statistics']},
 {id:'ATP',sport:'TENNIS',url:'https://www.atptour.com/',type:'TOUR',domains:['schedule','results','statistics']},
 {id:'WTA',sport:'TENNIS',url:'https://www.wtatennis.com/',type:'TOUR',domains:['schedule','results','statistics']},
 {id:'NBA',sport:'NBA',url:'https://www.nba.com/',type:'LEAGUE',domains:['schedule','results','statistics','roster']},
 {id:'NBA_REPORT',sport:'NBA',url:'https://official.nba.com/',type:'LEAGUE',domains:['availability']},
 {id:'ESPN',sport:'NBA',url:'https://www.espn.com/nba/',type:'SECONDARY',domains:['schedule','results','statistics']}
].map(x=>Object.freeze({...x,domains:Object.freeze(x.domains),access:'NOT_CHECKED'})));
export const freshness=Object.freeze({FOOTBALL:{schedule:24,results:24,statistics:168,roster:24,availability:6},TENNIS:{schedule:12,results:24,statistics:168,availability:6},NBA:{schedule:12,results:24,statistics:168,roster:24,availability:3}});
export function receiveData(input){
 const lock={readiness:'BLOCKED',verification:'NOT_PERFORMED',engine_access:false,markets:'NOT_EVALUATED'};
 if(!input||!['REAL','SYNTHETIC'].includes(input.dataset_kind)||!Object.hasOwn(freshness,input.sport)||!Array.isArray(input.records)||!input.records.length||input.records.length>100||!Number.isFinite(Date.parse(input.as_of)))return {...lock,valid:false,rows:[],status:'REJECTED'};
 const rows=input.records.map(r=>{
 r=r&&typeof r==='object'?r:{};const flags=[];const source=sources.find(s=>s.id===r.source_id&&s.sport===input.sport);
 if(!source)flags.push('UNKNOWN_SOURCE');else if(!source.domains.includes(r.domain))flags.push('DOMAIN_NOT_DECLARED');
 for(const k of ['reference','subject','metric','period','unit'])if(typeof r[k]!=='string'||!r[k].trim())flags.push('MISSING_'+k.toUpperCase());
 if(!Number.isFinite(r.value))flags.push('INVALID_VALUE');
 const hours=(Date.parse(input.as_of)-Date.parse(r.collected_at))/3600000,limit=Object.hasOwn(freshness[input.sport],r.domain)?freshness[input.sport][r.domain]:null;
 if(!Number.isFinite(hours)||hours<0)flags.push('INVALID_DATE');else if(limit===null)flags.push('NO_FRESHNESS_POLICY');else if(hours>limit)flags.push('REVIEW_FRESHNESS');
 return {source_id:r.source_id??null,source_type:source?.type??null,reference:r.reference??null,subject:r.subject??null,metric:r.metric??null,period:r.period??null,unit:r.unit??null,value:Number.isFinite(r.value)?r.value:null,collected_at:r.collected_at??null,age_hours:Number.isFinite(hours)?hours:null,flags,verified:false};
 });
 return {...lock,valid:true,dataset_kind:input.dataset_kind,sport:input.sport,rows,status:rows.some(r=>r.flags.length)?'QUARANTINE_REVIEW':'QUARANTINE_UNVERIFIED',policy:'EXPERIMENTAL_REVIEW_WINDOWS'};
}
export function runIntakeDemo(){
 const base={dataset_kind:'SYNTHETIC',sport:'NBA',as_of:'2026-11-24T06:00:00Z',records:[{source_id:'NBA',domain:'statistics',reference:'SIM-1',subject:'SIM-TEAM',metric:'points',period:'SIM-P1',unit:'points',value:110,collected_at:'2026-11-24T00:00:00Z'}]};
 const patch=(p)=>({...base,records:[{...base.records[0],...p}]});
 const cases=[['DIRECTORY',()=>sources.length===8&&sources.every(s=>s.access==='NOT_CHECKED')],['COMPLETE',()=>receiveData(base).status==='QUARANTINE_UNVERIFIED'],['UNKNOWN_SOURCE',()=>receiveData(patch({source_id:'UNKNOWN'})).rows[0].flags.includes('UNKNOWN_SOURCE')],['STALE',()=>receiveData(patch({collected_at:'2026-11-01T00:00:00Z'})).rows[0].flags.includes('REVIEW_FRESHNESS')],['MISSING_REFERENCE',()=>receiveData(patch({reference:''})).rows[0].flags.includes('MISSING_REFERENCE')],['REAL_ISOLATION',()=>{const r=receiveData({...base,dataset_kind:'REAL'});return r.valid&&!r.engine_access&&r.verification==='NOT_PERFORMED'&&r.readiness==='BLOCKED'}],['DOMAIN_MISMATCH',()=>receiveData(patch({domain:'availability'})).rows[0].flags.includes('DOMAIN_NOT_DECLARED')]];
 return cases.map(([id,check])=>({id,pass:check()}));
}
