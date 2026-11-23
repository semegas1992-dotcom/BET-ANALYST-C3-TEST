// C3.38–C3.43: synthetic evidence sheets; no sport-specific forecasting.
import {auditSportIndicators} from './c3-35-37-indicators.js';
const groups={FOOTBALL:'COLLECTIVE',TENNIS:'INDIVIDUAL',NBA:'COLLECTIVE'};
export function buildSyntheticSheet(input){
 const audit=auditSportIndicators(input);
 if(!audit.valid)return {valid:false,errors:audit.issues,readiness:'BLOCKED',sheet:null};
 const issues=[...audit.warnings],rows=[];
 for(let i=0;i<audit.indicators.length;i++){
  const x=audit.indicators[i],m=input.measures[i];
  const period=typeof m.period==='string'&&m.period.trim()?m.period.trim():null;
  const samePeriod=typeof m.period_home==='string'&&typeof m.period_away==='string'&&m.period_home===m.period_away;
  const periodComparable=period!==null&&(m.period_home===undefined&&m.period_away===undefined||samePeriod);
  const sampleComparable=Number.isInteger(m.sample_size_home)&&Number.isInteger(m.sample_size_away)&&m.sample_size_home>0&&m.sample_size_away>0&&m.sample_size_home===m.sample_size_away;
  const provenance=m.evidence&&typeof m.evidence==='object'?{source_label:m.evidence.source_label??null,reference:m.evidence.reference??null,collected_at:m.evidence.collected_at??null,independently_verified:false}:{source_label:null,reference:null,collected_at:null,independently_verified:false};
  const completeProvenance=Boolean(provenance.source_label&&provenance.reference&&provenance.collected_at);
  const flags=[];
  if(!periodComparable)flags.push('PERIOD_NOT_COMPARABLE');
  if(!sampleComparable)flags.push('SAMPLE_NOT_COMPARABLE');
  if(!completeProvenance)flags.push('PROVENANCE_INCOMPLETE');
  if(m.comparable!==true)flags.push('COMPARABILITY_NOT_ATTESTED');
  if(flags.length)issues.push(...flags.map(f=>x.id+':'+f));
  rows.push({id:x.id,category:x.category,scope:groups[input.sport],difference:x.difference,unit:x.unit,arithmetic_direction:x.arithmetic_direction,
   sample_home:m.sample_size_home??null,sample_away:m.sample_size_away??null,period,period_comparable:periodComparable,sample_comparable:sampleComparable,
   provenance,flags,status:flags.length?'REQUIRES_REVIEW':'DOCUMENTED_NOT_VERIFIED'});
 }
 const comparable=rows.filter(x=>x.status==='DOCUMENTED_NOT_VERIFIED').length;
 return {valid:true,schema:'BET_ANALYST_SYNTHETIC_SHEET_V1',sport:input.sport,match_id:input.match_id,rows,
  summary:{total:rows.length,documented_not_verified:comparable,requires_review:rows.length-comparable,mixed_directions:audit.summary.mixed_directions},
  issues:[...new Set(issues)],readiness:'BLOCKED',rapport_de_force:'NOT_COMPUTED',scenarios:'NOT_COMPUTED',probabilities:'NOT_COMPUTED',markets:'NOT_EVALUATED',
  limits:['Synthetic only','No independent verification','No sport-specific inference']};
}
const m=(id,home,away,unit,direction)=>({id,label:'Mesure fictive '+id,home,away,unit,direction,sample_size_home:12,sample_size_away:12,period:'12 matchs fictifs',comparable:true,evidence:{source_label:'Simulation interne',reference:'SIM-'+id,collected_at:'2026-11-23'}});
export function runSyntheticSheetDemo(){
 const football={dataset_kind:'SYNTHETIC',sport:'FOOTBALL',match_id:'C343-F',measures:[m('shots',12,9,'tirs','HIGHER_BETTER'),m('conceded',1.4,1.1,'buts','LOWER_BETTER')]};
 const tennis={dataset_kind:'SYNTHETIC',sport:'TENNIS',match_id:'C343-T',measures:[m('aces',8,5,'aces','HIGHER_BETTER')]};
 const nba={dataset_kind:'SYNTHETIC',sport:'NBA',match_id:'C343-N',measures:[m('points',115,110,'points','HIGHER_BETTER')]};
 nba.measures[0].sample_size_away=8;
 const real={...football,dataset_kind:'REAL'};
 const cases=[{id:'FOOTBALL_SHEET',input:football,expected_rows:2,expected_review:0},
 {id:'TENNIS_INDIVIDUAL',input:tennis,expected_rows:1,expected_review:0},
 {id:'NBA_SAMPLE_MISMATCH',input:nba,expected_rows:1,expected_review:1},
 {id:'REAL_REJECTED',input:real,expected_rejected:true}];
 return {cases:cases.map(c=>{const result=buildSyntheticSheet(c.input);const pass=c.expected_rejected?!result.valid&&result.readiness==='BLOCKED':result.valid&&result.summary.total===c.expected_rows&&result.summary.requires_review===c.expected_review&&result.readiness==='BLOCKED'&&result.probabilities==='NOT_COMPUTED';return {id:c.id,pass,result}})};
}
