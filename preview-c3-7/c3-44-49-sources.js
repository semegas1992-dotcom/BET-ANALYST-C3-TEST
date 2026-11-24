// Synthetic source audit. No external retrieval or verification.
export function auditSources(input){
 const blocked={readiness:'BLOCKED',verification:'NOT_PERFORMED',markets:'NOT_EVALUATED'};
 if(input?.dataset_kind!=='SYNTHETIC'||!Array.isArray(input.records)||!input.records.length||!Number.isFinite(Date.parse(input.as_of)))return {...blocked,valid:false,issues:['INVALID_OR_REAL_INPUT']};
 const issues=[],rows=[],seen=new Map(),now=Date.parse(input.as_of);
 for(const r of input.records){
 if(!r||typeof r!=='object'){issues.push('INVALID_RECORD');continue}
 const flags=[];
 if(typeof r.source!=='string'||!r.source.trim()||typeof r.reference!=='string'||!r.reference.trim())flags.push('MISSING_PROVENANCE');
 const t=Date.parse(r.collected_at);
 if(!Number.isFinite(t)||t>now)flags.push('INVALID_DATE');
 else if(now-t>86400000)flags.push('STALE_SYNTHETIC_WINDOW');
 if(typeof r.metric!=='string'||!r.metric.trim()||typeof r.period!=='string'||!r.period.trim()||typeof r.unit!=='string'||!r.unit.trim()||!Number.isFinite(r.value))flags.push('INVALID_MEASURE');
 else {const k=JSON.stringify([r.metric,r.period,r.unit]);if(seen.has(k)&&seen.get(k)!==r.value)flags.push('CONFLICTING_VALUES');else seen.set(k,r.value)}
 issues.push(...flags);rows.push({source:r.source??null,reference:r.reference??null,flags,independently_verified:false});
 }
 return {...blocked,valid:true,rows,issues:[...new Set(issues)],status:issues.length?'REQUIRES_REVIEW':'DECLARED_NOT_VERIFIED'};
}
export function runSourceAuditDemo(){
 const base={source:'SIM-A',reference:'FIXTURE-1',collected_at:'2026-11-24T00:00:00Z',metric:'points',period:'fixture',unit:'points',value:110};
 const cases=[['COMPLETE',[base],null],['MISSING_REFERENCE',[{...base,reference:''}],'MISSING_PROVENANCE'],['STALE',[{...base,collected_at:'2026-11-20T00:00:00Z'}],'STALE_SYNTHETIC_WINDOW'],['FUTURE',[{...base,collected_at:'2026-11-25T00:00:00Z'}],'INVALID_DATE'],['CONFLICT',[base,{...base,source:'SIM-B',value:115}],'CONFLICTING_VALUES'],['REAL_REJECTED',[base],'INVALID_OR_REAL_INPUT']];
 return cases.map(([id,records,expected])=>{const result=auditSources({dataset_kind:id==='REAL_REJECTED'?'REAL':'SYNTHETIC',as_of:'2026-11-24T06:00:00Z',records});return {id,result,pass:result.readiness==='BLOCKED'&&result.verification==='NOT_PERFORMED'&&(expected?result.issues.includes(expected):result.status==='DECLARED_NOT_VERIFIED')}});
}
