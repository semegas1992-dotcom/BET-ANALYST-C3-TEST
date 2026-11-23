// C3.20–C3.22 — contrôles expérimentaux isolés, données fictives uniquement.
import {compareControlledMeasures} from './c3-17-controlled-measures.js';
import {auditControlledMeasures} from './c3-18-measure-quality.js';
import {assessSyntheticBalance} from './c3-19-synthetic-balance.js';
export function inspectSyntheticEvidence(input){
 const base=compareControlledMeasures(input);
 if(!base.valid)return {valid:false,errors:base.errors,analysis_readiness:'BLOCKED'};
 const audit=auditControlledMeasures(input),balance=assessSyntheticBalance(input);
 const checks=base.comparisons.map((m,i)=>{
  const original=input.measures[i],issues=[];
  if(original.period===undefined)issues.push('PERIOD_NOT_DECLARED');
  else if(typeof original.period!=='string'||!original.period.trim())issues.push('INVALID_PERIOD');
  if(original.sample_size_home===undefined||original.sample_size_away===undefined)issues.push('SAMPLE_SIZE_NOT_DECLARED');
  if(original.unit_home!==undefined&&original.unit_home!==m.unit)issues.push('UNIT_MISMATCH_HOME');
  if(original.unit_away!==undefined&&original.unit_away!==m.unit)issues.push('UNIT_MISMATCH_AWAY');
  if(original.comparable===false)issues.push('COMPARABILITY_DENIED');
  if(original.comparable!==true)issues.push('COMPARABILITY_NOT_ATTESTED');
  return {id:m.id,issues,comparable_for_model:issues.length===0};
 });
 const scenarios=[
  {id:'A',hypothesis:'Les indicateurs favorables au domicile conservent leur orientation',status:'CONDITIONAL_UNQUANTIFIED'},
  {id:'B',hypothesis:'Les indicateurs favorables à l’extérieur conservent leur orientation',status:'CONDITIONAL_UNQUANTIFIED'},
  {id:'C',hypothesis:'Les signaux contradictoires ou neutres empêchent de trancher',status:'CONDITIONAL_UNQUANTIFIED'}
 ];
 const sensitivity=base.comparisons.map((removed,i)=>{
  const remaining=base.comparisons.filter((_,j)=>j!==i);
  const home=remaining.filter(x=>x.preferred==='HOME').length,away=remaining.filter(x=>x.preferred==='AWAY').length;
  return {removed_id:removed.id,remaining_home:home,remaining_away:away,remaining_equal:remaining.filter(x=>x.preferred==='EQUAL').length,has_opposing_signals:home>0&&away>0};
 });
 const conflicts=checks.flatMap(x=>x.issues.map(issue=>({id:x.id,issue})));
 return {schema:'BET_ANALYST_SYNTHETIC_CONTROLS_V1',valid:true,match_id:base.match_id,
  checks,conflicts,scenarios,sensitivity,
  status:'EXPERIMENTAL_NOT_CERTIFIED',balance_status:balance.status,
  dominant_team:null,probabilities:'NOT_COMPUTED',rapport_de_force:'NOT_COMPUTED',
  markets:'NOT_EVALUATED',analysis_readiness:'BLOCKED',
  limitations:['Aucune validation indépendante','Scénarios hypothétiques sans probabilité','Retrait d’indicateur sans pondération ni estimation de robustesse sportive','Aucun moteur KRAFT']};
}
