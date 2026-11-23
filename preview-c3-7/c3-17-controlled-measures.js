// C3.17 — moteur expérimental de comparaison de mesures fictives.
// Ne constitue pas KRAFT V3.0 ; aucun calcul sur les preuves déclaratives C3.11.
const OWN=Object.prototype.hasOwnProperty;
const finite=n=>typeof n==='number'&&Number.isFinite(n);
export function compareControlledMeasures(input){
 const errors=[];
 if(!input||typeof input!=='object'||Array.isArray(input))return {valid:false,errors:['INVALID_INPUT'],analysis_readiness:'BLOCKED',comparison:null};
 if(input.schema!=='BET_ANALYST_CONTROLLED_MEASURES_V1')errors.push('INVALID_SCHEMA');
 if(input.dataset_kind!=='SYNTHETIC')errors.push('SYNTHETIC_ONLY');
 if(typeof input.match_id!=='string'||!input.match_id.trim())errors.push('INVALID_MATCH_ID');
 if(!Array.isArray(input.measures)||input.measures.length===0||input.measures.length>20)errors.push('INVALID_MEASURES');
 const measures=Array.isArray(input.measures)?input.measures:[];
 const ids=new Set();
 for(let i=0;i<measures.length;i++){
  const m=measures[i];
  if(!m||typeof m!=='object'||Array.isArray(m)){errors.push('INVALID_MEASURE_'+i);continue}
  if(typeof m.id!=='string'||!m.id.trim()||ids.has(m.id))errors.push('INVALID_OR_DUPLICATE_ID_'+i);else ids.add(m.id);
  if(typeof m.label!=='string'||!m.label.trim())errors.push('INVALID_LABEL_'+i);
  if(!finite(m.home)||!finite(m.away))errors.push('INVALID_NUMERIC_VALUE_'+i);
  if(typeof m.unit!=='string'||!m.unit.trim())errors.push('INVALID_UNIT_'+i);
  if(m.direction!=='HIGHER_BETTER'&&m.direction!=='LOWER_BETTER')errors.push('INVALID_DIRECTION_'+i);
  if(m.sample_size_home!==undefined&&(!Number.isInteger(m.sample_size_home)||m.sample_size_home<1))errors.push('INVALID_SAMPLE_HOME_'+i);
  if(m.sample_size_away!==undefined&&(!Number.isInteger(m.sample_size_away)||m.sample_size_away<1))errors.push('INVALID_SAMPLE_AWAY_'+i);
 }
 if(errors.length)return {valid:false,errors,analysis_readiness:'BLOCKED',comparison:null};
 const comparisons=measures.map(m=>{
  const difference=m.home-m.away;
  const preferred=difference===0?'EQUAL':((difference>0)===(m.direction==='HIGHER_BETTER')?'HOME':'AWAY');
  return {id:m.id,label:m.label,unit:m.unit,home:m.home,away:m.away,difference,preferred,
   sample_size_home:m.sample_size_home??null,sample_size_away:m.sample_size_away??null};
 });
 return {schema:'BET_ANALYST_MEASURE_COMPARISON_V1',valid:true,errors:[],match_id:input.match_id,
  comparisons,analysis_readiness:'BLOCKED',rapport_de_force:'NOT_COMPUTED',
  scenarios:['A','B','C'].map(id=>({id,status:'NOT_COMPUTED'})),
  probabilities:'NOT_COMPUTED',markets:'NOT_EVALUATED',
  limitations:['Mesures fictives uniquement','Comparaison arithmétique sans pondération ni modèle sportif','Aucune validation indépendante','Aucune projection ni recommandation de marché']};
}
