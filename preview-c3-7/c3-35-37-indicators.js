// C3.35–C3.37 — descriptive multi-indicator audit on fictional inputs only.
import {describeSyntheticSport} from './c3-32-34-descriptive.js';
const group={FOOTBALL:{shots:'COLLECTIVE',conceded:'COLLECTIVE',possession:'COLLECTIVE'},TENNIS:{first_serve_pct:'INDIVIDUAL',aces:'INDIVIDUAL',double_faults:'INDIVIDUAL'},NBA:{points:'COLLECTIVE',rebounds:'COLLECTIVE',turnovers:'COLLECTIVE'}};
export function auditSportIndicators(input){
 const r=describeSyntheticSport(input);
 if(!r.valid)return {valid:false,issues:r.issues,warnings:r.warnings,readiness:'BLOCKED',indicators:[],summary:null};
 const indicators=r.comparisons.map((m,i)=>({id:m.id,category:group[input.sport][m.id],difference:m.difference,unit:m.unit,arithmetic_direction:m.preferred,
  quality:input.measures[i].comparable===true&&Number.isInteger(input.measures[i].sample_size_home)&&input.measures[i].sample_size_home>0&&Number.isInteger(input.measures[i].sample_size_away)&&input.measures[i].sample_size_away>0&&typeof input.measures[i].period==='string'&&input.measures[i].period.trim()?'DOCUMENTED_NOT_VERIFIED':'REQUIRES_DOCUMENTATION'}));
 const documented=indicators.filter(x=>x.quality==='DOCUMENTED_NOT_VERIFIED').length;
 return {schema:'BET_ANALYST_INDICATOR_AUDIT_V1',valid:true,sport:input.sport,indicators,
  summary:{total:indicators.length,documented,requires_documentation:indicators.length-documented,mixed_directions:r.contradictions,counts:r.signal_counts},
  warnings:r.warnings,readiness:'BLOCKED',inference:'NOT_PERMITTED',probabilities:'NOT_COMPUTED',markets:'NOT_EVALUATED'};
}
const measure=(id,home,away,unit,direction)=>({id,label:'Fictif '+id,home,away,unit,direction,sample_size_home:12,sample_size_away:12,period:'12 matchs fictifs',comparable:true});
const base=(sport,measures)=>({dataset_kind:'SYNTHETIC',sport,match_id:'C335-'+sport,measures});
export function runIndicatorAuditDemo(){
 const cases=[
  {id:'FOOTBALL_MULTI',input:base('FOOTBALL',[measure('shots',12,9,'tirs','HIGHER_BETTER'),measure('conceded',1.5,1,'buts','LOWER_BETTER')]),expected_mixed:true},
  {id:'TENNIS_MULTI',input:base('TENNIS',[measure('aces',8,5,'aces','HIGHER_BETTER'),measure('double_faults',3,5,'fautes','LOWER_BETTER')]),expected_mixed:false},
  {id:'NBA_MISSING_PERIOD',input:base('NBA',[measure('points',115,110,'points','HIGHER_BETTER'),measure('rebounds',42,40,'rebonds','HIGHER_BETTER')]),expected_missing:1},
  {id:'REAL_REJECTED',input:{dataset_kind:'REAL',sport:'NBA',match_id:'REAL',measures:[]},expected_rejected:true}
 ];
 delete cases[2].input.measures[1].period;
 return {cases:cases.map(c=>{const r=auditSportIndicators(c.input);return {id:c.id,pass:c.expected_rejected?!r.valid&&r.readiness==='BLOCKED':r.valid&&r.readiness==='BLOCKED'&&r.inference==='NOT_PERMITTED'&&r.summary.total===2&&(c.expected_mixed===undefined||r.summary.mixed_directions===c.expected_mixed)&&(c.expected_missing===undefined||r.summary.requires_documentation===c.expected_missing),result:r}})};
}
