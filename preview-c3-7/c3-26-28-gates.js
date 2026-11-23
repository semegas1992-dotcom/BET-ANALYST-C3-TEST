// C3.26–C3.28 — banc d'essai déterministe, sans réseau ni données sportives réelles.
import {summarizeSyntheticEvidence} from './c3-23-25-report.js';
const m=(id,home,away,direction='HIGHER_BETTER')=>({id,label:'Mesure fictive '+id,home,away,unit:'unités fictives',direction,sample_size_home:20,sample_size_away:20,period:'20 matchs fictifs',comparable:true,evidence:{source_label:'Simulation interne',reference:'SIM-'+id,collected_at:'2026-11-23',status:'DECLARED'}});
const base=measures=>({schema:'BET_ANALYST_CONTROLLED_MEASURES_V1',dataset_kind:'SYNTHETIC',match_id:'LAB-C326',measures});
export function syntheticFixtures(){
 const complete=base([m('one',12,9),m('two',8,6)]);
 const incomplete=base([m('one',12,9),m('two',8,6)]);delete incomplete.measures[0].period;delete incomplete.measures[1].evidence;
 const inconsistent=base([m('one',12,9),m('two',8,6)]);inconsistent.measures[0].unit_home='unités incompatibles';inconsistent.measures[1].comparable=false;
 const opposed=base([m('one',12,9),m('two',8,6,'LOWER_BETTER')]);
 const invalid=base([m('one',12,9)]);invalid.dataset_kind='REAL';
 return [{id:'COMPLETE_DECLARED',input:complete,expected_valid:true},
 {id:'INCOMPLETE',input:incomplete,expected_valid:true},
 {id:'INCONSISTENT',input:inconsistent,expected_valid:true},
 {id:'OPPOSING_SIGNALS',input:opposed,expected_valid:true},
 {id:'REAL_REJECTED',input:invalid,expected_valid:false}];
}
export function runSyntheticGateSuite(){
 const cases=syntheticFixtures().map(f=>{
  const r=summarizeSyntheticEvidence(f.input);
  const valid=r.valid===f.expected_valid;
  const blocked=r.analysis_readiness==='BLOCKED';
  const noInference=!r.valid||r.report.dominant_team===null&&r.report.probabilities==='NOT_COMPUTED'&&r.report.markets==='NOT_EVALUATED';
  const evidenceOnly=f.id!=='COMPLETE_DECLARED'||r.trace.every(x=>x.independently_verified===false);
  const specific=f.id==='INCOMPLETE'?r.conflicts.some(x=>x.issue==='PERIOD_NOT_DECLARED')&&r.conflicts.some(x=>x.issue==='EVIDENCE_NOT_DECLARED'):
   f.id==='INCONSISTENT'?r.conflicts.some(x=>x.issue==='UNIT_MISMATCH_HOME')&&r.conflicts.some(x=>x.issue==='COMPARABILITY_DENIED'):
   f.id==='OPPOSING_SIGNALS'?r.category_counts.INDICATOR_DISAGREEMENT===1:
   f.id==='REAL_REJECTED'?!r.valid:r.report.traceable_measurements===2;
  return {id:f.id,pass:valid&&blocked&&noInference&&evidenceOnly&&specific,valid:r.valid,
   blocked,traceable:r.valid?r.report.traceable_measurements:null,
   conflicts:r.valid?r.conflicts.length:null,notes:r.valid?'Déclarations fictives, sans certification externe':'Entrée refusée'};
 });
 return {schema:'BET_ANALYST_SYNTHETIC_GATE_SUITE_V1',cases,passed:cases.filter(x=>x.pass).length,total:cases.length,
  all_pass:cases.every(x=>x.pass),analysis_readiness:'BLOCKED',
  preparation:{input_validation:'EXPERIMENTAL',documentary_controls:'EXPERIMENTAL',
   source_verification:'NOT_IMPLEMENTED',sporting_model:'NOT_IMPLEMENTED',
   calibrated_probabilities:'NOT_IMPLEMENTED',kraft_engine:'NOT_IMPLEMENTED',
   next_gate:'TEST_RUNNER_AND_REAL_EVIDENCE_VERIFICATION_REQUIRED'},
  limitations:['Essais fictifs uniquement','Contrôles de non-régression partiels, pas la totalité de la CI','Aucune validation externe ni calcul sportif']};
}
