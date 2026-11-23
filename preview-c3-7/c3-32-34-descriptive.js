// C3.32–C3.34 — descriptif synthétique uniquement; pas de projection ni de modèle KRAFT.
import {compareControlledMeasures} from './c3-17-controlled-measures.js';
import {inspectEngineContract} from './c3-29-31-contract.js';
const SPORT_METRICS={FOOTBALL:['shots','conceded','possession'],TENNIS:['first_serve_pct','aces','double_faults'],NBA:['points','rebounds','turnovers']};
const METRIC_UNITS={shots:'tirs',conceded:'buts',possession:'%',first_serve_pct:'%',aces:'aces',double_faults:'fautes',points:'points',rebounds:'rebonds',turnovers:'pertes'};
export function describeSyntheticSport(input){
 const contract=inspectEngineContract(input),issues=[...contract.errors],warnings=[...contract.warnings];
 if(!contract.valid)return {valid:false,issues,warnings,analysis_readiness:'BLOCKED',comparisons:[],outputs:'NOT_COMPUTED'};
 const allowed=SPORT_METRICS[input.sport],measures=input.measures;
 if(measures.length>20)issues.push('TOO_MANY_MEASURES');
 for(const [i,m] of measures.entries()){
  if(!allowed.includes(m.id))issues.push('UNSUPPORTED_METRIC:'+i);
  if(m.unit!==METRIC_UNITS[m.id])issues.push('UNIT_NOT_NORMALIZED:'+i);
  if(typeof m.label!=='string'||!m.label.trim())issues.push('LABEL_REQUIRED:'+i);
  if(!Number.isInteger(m.sample_size_home)||m.sample_size_home<1||!Number.isInteger(m.sample_size_away)||m.sample_size_away<1)warnings.push('SAMPLE_NOT_DOCUMENTED:'+i);
  if(typeof m.period!=='string'||!m.period.trim())warnings.push('PERIOD_NOT_DOCUMENTED:'+i);
  if(m.comparable!==true)warnings.push('COMPARABILITY_NOT_ATTESTED:'+i);
 }
 if(issues.length)return {valid:false,issues,warnings,analysis_readiness:'BLOCKED',comparisons:[],outputs:'NOT_COMPUTED'};
 const raw=compareControlledMeasures({...input,schema:'BET_ANALYST_CONTROLLED_MEASURES_V1'});
 if(!raw.valid)return {valid:false,issues:raw.errors,warnings,analysis_readiness:'BLOCKED',comparisons:[],outputs:'NOT_COMPUTED'};
 const comparisons=raw.comparisons.map(m=>({id:m.id,home:m.home,away:m.away,unit:m.unit,difference:m.difference,preferred:m.preferred,interpretation:'ARITHMETIC_ONLY'}));
 const home=comparisons.filter(x=>x.preferred==='HOME').length,away=comparisons.filter(x=>x.preferred==='AWAY').length;
 const contradictions=home>0&&away>0;
 if(contradictions)warnings.push('MIXED_INDICATOR_DIRECTIONS');
 return {schema:'BET_ANALYST_SYNTHETIC_SPORT_DESCRIPTION_V1',valid:true,sport:input.sport,issues,warnings,
  comparisons,signal_counts:{home,away,equal:comparisons.length-home-away},contradictions,
  data_status:warnings.length?'DOCUMENTARY_RESERVATIONS':'DECLARED_COMPLETE_NOT_VERIFIED',
  outputs:{rapport_de_force:'NOT_COMPUTED',scenarios_abc:'NOT_COMPUTED',probabilities:'NOT_COMPUTED',markets:'NOT_EVALUATED'},
  analysis_readiness:'BLOCKED',calculation_allowed:false,
  limitations:['Données fictives uniquement','Écarts arithmétiques descriptifs','Aucune inférence sportive ni pondération','Sources non vérifiées indépendamment']};
}
export function runSportDescriptionDemo(){
 const cases=[
  ['FOOTBALL','shots',12,9,'tirs','HIGHER_BETTER'],
  ['TENNIS','aces',8,5,'aces','HIGHER_BETTER'],
  ['NBA','points',115,110,'points','HIGHER_BETTER']
 ].map(([sport,id,home,away,unit,direction])=>{
  const result=describeSyntheticSport({dataset_kind:'SYNTHETIC',sport,match_id:'SYN-'+sport,measures:[{id,label:'Mesure fictive',home,away,unit,direction,sample_size_home:10,sample_size_away:10,period:'10 matchs fictifs',comparable:true}]});
  return {sport,pass:result.valid&&result.comparisons.length===1&&result.comparisons[0].difference===home-away&&result.analysis_readiness==='BLOCKED'&&result.outputs.probabilities==='NOT_COMPUTED',result};
 });
 const real=describeSyntheticSport({dataset_kind:'REAL',sport:'NBA',match_id:'NO',measures:[]});
 return {cases,real_rejected:!real.valid&&real.analysis_readiness==='BLOCKED',passed:cases.filter(x=>x.pass).length,total:cases.length,analysis_readiness:'BLOCKED'};
}
