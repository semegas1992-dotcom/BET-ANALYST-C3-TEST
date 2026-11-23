// C3.19 — évaluation expérimentale du rapport de force sur données fictives.
// Aucun calcul de probabilité, aucune projection et aucune implémentation KRAFT.
import {auditControlledMeasures} from './c3-18-measure-quality.js';
export function assessSyntheticBalance(input){
 const audit=auditControlledMeasures(input);
 if(!audit.valid)return {schema:'BET_ANALYST_SYNTHETIC_BALANCE_V1',valid:false,errors:audit.errors,status:'REJECTED',analysis_readiness:'BLOCKED',interpretation:null};
 const issues=[];
 if(audit.items.length<2)issues.push('INSUFFICIENT_INDICATOR_COUNT');
 if(audit.signals.includes('UNKNOWN_SAMPLE_SIZES'))issues.push('UNKNOWN_SAMPLE_SIZES');
 if(audit.signals.includes('LIMITED_SAMPLE_SIZES'))issues.push('LIMITED_SAMPLE_SIZES');
 if(audit.signals.includes('MIXED_DIRECTIONS'))issues.push('MIXED_DIRECTIONS');
 const decisive=audit.counts.home+audit.counts.away;
 if(decisive===0)issues.push('NO_DIRECTIONAL_SIGNAL');
 // Les indicateurs ne sont ni indépendants ni comparables en importance.
 // Même sans alerte, aucune supériorité sportive n'est inférée.
 return {schema:'BET_ANALYST_SYNTHETIC_BALANCE_V1',valid:true,match_id:audit.match_id,
  status:issues.length?'INDETERMINATE_WITH_ALERTS':'INDETERMINATE_NO_CERTIFIED_MODEL',
  issues,indicator_counts:audit.counts,indicator_count:audit.items.length,
  interpretation:'UNDETERMINED',dominant_team:null,
  rapport_de_force:'NOT_COMPUTED',scenarios:'NOT_COMPUTED',markets:'NOT_EVALUATED',
  analysis_readiness:'BLOCKED',
  limitations:['Aucune pondération justifiée des indicateurs','Corrélations non évaluées','Aucune validation externe','Les tailles d’échantillon ne prouvent pas leur représentativité','Pas de modèle KRAFT opérationnel']};
}
