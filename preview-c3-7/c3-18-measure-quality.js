// C3.18 — audit de la robustesse documentaire des comparaisons fictives.
// Les seuils ci-dessous sont des règles d'essai techniques, pas des seuils KRAFT.
import {compareControlledMeasures} from './c3-17-controlled-measures.js';
export function auditControlledMeasures(input){
 const comparison=compareControlledMeasures(input);
 if(!comparison.valid)return {valid:false,errors:comparison.errors,analysis_readiness:'BLOCKED',items:[],signals:[]};
 const items=comparison.comparisons.map(m=>{
  const sizesKnown=m.sample_size_home!==null&&m.sample_size_away!==null;
  const minSample=sizesKnown?Math.min(m.sample_size_home,m.sample_size_away):null;
  const sample_status=!sizesKnown?'UNKNOWN':minSample<5?'VERY_SMALL':minSample<10?'LIMITED':'DOCUMENTED_SIZE_ONLY';
  return {id:m.id,preferred:m.preferred,sample_status,min_sample:minSample,
   limitation:sample_status==='DOCUMENTED_SIZE_ONLY'?'Taille déclarée, représentativité non démontrée':sample_status==='UNKNOWN'?'Échantillon non renseigné':'Échantillon limité selon seuil expérimental'};
 });
 const home=items.filter(x=>x.preferred==='HOME').length,away=items.filter(x=>x.preferred==='AWAY').length;
 const signals=[];
 if(home>0&&away>0)signals.push('MIXED_DIRECTIONS');
 if(items.some(x=>x.sample_status==='UNKNOWN'))signals.push('UNKNOWN_SAMPLE_SIZES');
 if(items.some(x=>x.sample_status==='VERY_SMALL'||x.sample_status==='LIMITED'))signals.push('LIMITED_SAMPLE_SIZES');
 return {schema:'BET_ANALYST_MEASURE_QUALITY_V1',valid:true,errors:[],match_id:comparison.match_id,items,signals,
  counts:{home,away,equal:items.filter(x=>x.preferred==='EQUAL').length},
  analysis_readiness:'BLOCKED',rapport_de_force:'NOT_COMPUTED',scenarios:'NOT_COMPUTED',
  limitation:'Contrôles indicatifs sur mesures fictives, sans fiabilité sportive, pondération ni inférence de résultat.'};
}
