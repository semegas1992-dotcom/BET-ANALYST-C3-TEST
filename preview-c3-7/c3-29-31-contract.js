// C3.29–C3.31: architecture contract only. No sports engine, no KRAFT.
const sports=['FOOTBALL','TENNIS','NBA'];
const outputs=['rapport_de_force','scenarios_abc','probabilities','markets'];
export function inspectEngineContract(input){
 const errors=[],warnings=[];
 if(!input||typeof input!=='object'||Array.isArray(input))return {schema:'BET_ANALYST_ENGINE_CONTRACT_V1',valid:false,errors:['INVALID_INPUT'],analysis_readiness:'BLOCKED',calculation_allowed:false};
 if(input.dataset_kind!=='SYNTHETIC')errors.push('SYNTHETIC_ONLY');
 if(!sports.includes(input.sport))errors.push('SPORT_NOT_SUPPORTED');
 if(typeof input.match_id!=='string'||!input.match_id.trim())errors.push('MATCH_ID_REQUIRED');
 if(!Array.isArray(input.measures)||input.measures.length===0)errors.push('MEASURES_REQUIRED');
 const records=Array.isArray(input.measures)?input.measures:[];
 for(let i=0;i<records.length;i++){
  const m=records[i];
  if(!m||typeof m!=='object'||Array.isArray(m)){errors.push('MEASURE_INVALID:'+i);continue}
  if(typeof m.id!=='string'||!m.id.trim())errors.push('MEASURE_ID_REQUIRED:'+i);
  if(!Number.isFinite(m.home)||!Number.isFinite(m.away))errors.push('FINITE_VALUES_REQUIRED:'+i);
  if(!['HIGHER_BETTER','LOWER_BETTER'].includes(m.direction))errors.push('DIRECTION_REQUIRED:'+i);
  if(!m.evidence||typeof m.evidence!=='object'||m.evidence.independently_verified!==true)warnings.push('SOURCE_NOT_INDEPENDENTLY_VERIFIED:'+i);
 }
 if(records.some((m,i)=>m&&records.findIndex(x=>x&&x.id===m.id)!==i))errors.push('DUPLICATE_MEASURE_ID');
 const valid=errors.length===0;
 return {schema:'BET_ANALYST_ENGINE_CONTRACT_V1',valid,errors,warnings,
  sport:valid?input.sport:null,match_id:valid?input.match_id:null,
  input_contract:{dataset_kind:'SYNTHETIC',sports,required_measure_fields:['id','home','away','direction'],source_status:'DECLARATIVE_ONLY'},
  output_contract:Object.fromEntries(outputs.map(x=>[x,'NOT_COMPUTED'])),
  calculation_allowed:false,analysis_readiness:'BLOCKED',
  gates:{C3_29:valid?'CONTRACT_ACCEPTED':'CONTRACT_REJECTED',C3_30:'OUTPUTS_LOCKED',C3_31:'ENGINE_NOT_IMPLEMENTED'},
  blockers:['SOURCE_VERIFICATION_NOT_IMPLEMENTED','SPORT_SPECIFIC_MODEL_NOT_IMPLEMENTED','CALIBRATION_NOT_IMPLEMENTED','KRAFT_NOT_IMPLEMENTED'],
  limitations:['A valid input contract does not certify sources','No sports inference or market recommendation']};
}
export function runEngineContractDemo(){
 const fixture={dataset_kind:'SYNTHETIC',sport:'FOOTBALL',match_id:'ARCH-DEMO-001',
  measures:[{id:'shots',home:12,away:9,direction:'HIGHER_BETTER',evidence:{status:'DECLARED'}}]};
 const accepted=inspectEngineContract(fixture);
 const rejected=inspectEngineContract({...fixture,dataset_kind:'REAL'});
 const unsupported=inspectEngineContract({...fixture,sport:'CRICKET'});
 return {accepted,rejected,unsupported,checks:[
  {id:'SYNTHETIC_CONTRACT',pass:accepted.valid&&!accepted.calculation_allowed&&accepted.warnings.length===1},
  {id:'REAL_DATA_REJECTION',pass:!rejected.valid&&rejected.errors.includes('SYNTHETIC_ONLY')},
  {id:'UNSUPPORTED_SPORT',pass:!unsupported.valid&&unsupported.errors.includes('SPORT_NOT_SUPPORTED')},
  {id:'OUTPUT_LOCK',pass:outputs.every(k=>accepted.output_contract[k]==='NOT_COMPUTED')&&accepted.analysis_readiness==='BLOCKED'}
 ]};
}
