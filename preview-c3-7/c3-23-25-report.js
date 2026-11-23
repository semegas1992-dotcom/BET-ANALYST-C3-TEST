// C3.23–C3.25 — provenance déclarative, typologie des réserves et synthèse fictive.
import {inspectSyntheticEvidence} from './c3-20-22-controls.js';
import {auditControlledMeasures} from './c3-18-measure-quality.js';
const OWN=Object.prototype.hasOwnProperty;
const nonempty=x=>typeof x==='string'&&x.trim().length>0;
const categories={
 PERIOD_NOT_DECLARED:'MISSING',SAMPLE_SIZE_NOT_DECLARED:'MISSING',COMPARABILITY_NOT_ATTESTED:'UNVERIFIED',
 INVALID_PERIOD:'INCONSISTENCY',UNIT_MISMATCH_HOME:'INCONSISTENCY',UNIT_MISMATCH_AWAY:'INCONSISTENCY',
 COMPARABILITY_DENIED:'INCONSISTENCY',MIXED_DIRECTIONS:'INDICATOR_DISAGREEMENT'
};
export function summarizeSyntheticEvidence(input){
 const core=inspectSyntheticEvidence(input);
 if(!core.valid)return {schema:'BET_ANALYST_SYNTHETIC_REPORT_V1',valid:false,errors:core.errors,analysis_readiness:'BLOCKED',report:null};
 const trace=core.checks.map((item,i)=>{
  const m=input.measures[i],issues=[];
  const evidence=OWN.call(m,'evidence')?m.evidence:null;
  if(evidence===null)issues.push('EVIDENCE_NOT_DECLARED');
  else if(!evidence||typeof evidence!=='object'||Array.isArray(evidence))issues.push('EVIDENCE_INVALID');
  else{
   if(!nonempty(evidence.source_label))issues.push('SOURCE_LABEL_MISSING');
   if(!nonempty(evidence.reference))issues.push('REFERENCE_MISSING');
   if(!nonempty(evidence.collected_at))issues.push('COLLECTION_DATE_MISSING');
   if(!['DECLARED','HYPOTHESIS','UNVERIFIED'].includes(evidence.status))issues.push('EVIDENCE_STATUS_INVALID');
  }
  return {id:item.id,source_label:evidence&&nonempty(evidence.source_label)?evidence.source_label:null,
   reference:evidence&&nonempty(evidence.reference)?evidence.reference:null,
   collected_at:evidence&&nonempty(evidence.collected_at)?evidence.collected_at:null,
   evidence_status:evidence&&typeof evidence.status==='string'?evidence.status:null,
   issues,independently_verified:false};
 });
 const conflicts=core.conflicts.map(x=>({...x,category:categories[x.issue]||'OTHER'}));
 const hasMixed=auditControlledMeasures(input).signals.includes('MIXED_DIRECTIONS');
 if(hasMixed)conflicts.push({id:null,issue:'MIXED_DIRECTIONS',category:'INDICATOR_DISAGREEMENT'});
 for(const t of trace)for(const issue of t.issues)conflicts.push({id:t.id,issue,category:issue==='EVIDENCE_NOT_DECLARED'||issue.endsWith('_MISSING')?'MISSING':issue==='EVIDENCE_INVALID'||issue==='EVIDENCE_STATUS_INVALID'?'INCONSISTENCY':'OTHER'});
 const count={MISSING:0,UNVERIFIED:0,INCONSISTENCY:0,INDICATOR_DISAGREEMENT:0,OTHER:0};
 for(const x of conflicts)count[x.category]=(count[x.category]||0)+1;
 return {schema:'BET_ANALYST_SYNTHETIC_REPORT_V1',valid:true,match_id:core.match_id,trace,conflicts,category_counts:count,
  report:{measurement_count:core.checks.length,traceable_measurements:trace.filter(x=>x.issues.length===0).length,
   documentary_reservations:core.conflicts.length,trace_reservations:trace.reduce((n,x)=>n+x.issues.length,0),
   sensitivity_runs:core.sensitivity.length,scenario_count:core.scenarios.length,
   status:'INSUFFICIENT_FOR_SPORTING_INFERENCE',dominant_team:null,probabilities:'NOT_COMPUTED',
   rapport_de_force:'NOT_COMPUTED',markets:'NOT_EVALUATED'},
  analysis_readiness:'BLOCKED',limitations:['Références uniquement déclarées, jamais vérifiées indépendamment','Un désaccord entre indicateurs n’est pas une incohérence documentaire','Aucun modèle sportif ni KRAFT']};
}
