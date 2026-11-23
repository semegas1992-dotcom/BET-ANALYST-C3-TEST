// C3.15-A — actions documentaires recommandées, sans déblocage automatique.
import {diagnoseMatch} from './c3-14-diagnostic.js';
const ACTIONS={
 INVALID_MATCH_SNAPSHOT:['Corriger le format de l’instantané','DATA'],
 SNAPSHOT_NOT_FRESH:['Importer un instantané plus récent','DATA'],
 MATCH_NOT_SELECTED_OR_FOUND:['Sélectionner une rencontre valide','DATA'],
 INVALID_EVIDENCE_DOSSIER:['Corriger la structure du dossier','DATA'],
 NO_MATCHING_DOSSIER:['Fournir un dossier avec le même identifiant de rencontre','DATA'],
 INCOMPLETE_PROVENANCE:['Documenter les sources et dates d’observation','DOCUMENTATION'],
 DOCUMENTARY_DIVERGENCES:['Examiner les valeurs divergentes sans trancher automatiquement','REVIEW'],
 MISSING_DECLARED_VERIFIED_DOMAINS:['Compléter les cinq domaines sportifs avec des éléments contrôlables','DATA'],
 NO_INDEPENDENT_SOURCE_VERIFICATION:['Mettre en place un contrôle indépendant des sources','VERIFICATION'],
 KRAFT_EXECUTION_NOT_IMPLEMENTED:['Développer et tester le moteur KRAFT séparément','ENGINE']
};
export function planRemediation(snapshot,dossier,selectedId,options={}){
 const diagnostic=diagnoseMatch(snapshot,dossier,selectedId,options);
 return {schema:'BET_ANALYST_REMEDIATION_V1',match_id:diagnostic.match_id,
  actions:diagnostic.reasons.map(reason=>({reason,description:ACTIONS[reason]?.[0]||'Examiner le contrôle concerné',category:ACTIONS[reason]?.[1]||'REVIEW',completed:false})),
  analysis_readiness:'BLOCKED',automatic_unlock:false,
  limitation:'Plan d’actions indicatif : aucune vérification externe ni exécution de KRAFT.'};
}
