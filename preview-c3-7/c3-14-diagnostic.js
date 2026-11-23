// C3.14-A — diagnostic documentaire consolidé, sans exécution KRAFT.
import {validateSnapshot} from './c3-5-snapshot.js';
import {validateKraftEvidence,REQUIRED_DOMAINS} from './c3-11-kraft-evidence.js';
import {linkMatchEvidence} from './c3-12-evidence-link.js';
import {auditEvidenceProvenance} from './c3-13-provenance.js';
import {classifyEvidence} from './c3-13-classification.js';
export function diagnoseMatch(snapshot,dossier,selectedId,options={}){
 const match=validateSnapshot(snapshot,options);
 const evidence=validateKraftEvidence(dossier);
 const reasons=[];
 const selected=match.usable&&match.matches.some(m=>String(m.id)===String(selectedId));
 if(!match.usable)reasons.push('INVALID_MATCH_SNAPSHOT');
 if(match.usable&&match.freshness!=='FRESH')reasons.push('SNAPSHOT_NOT_FRESH');
 if(!selected)reasons.push('MATCH_NOT_SELECTED_OR_FOUND');
 if(!evidence.valid)reasons.push('INVALID_EVIDENCE_DOSSIER');
 const link=linkMatchEvidence(snapshot,dossier,options);
 const associated=selected&&link.linked&&link.match.id===String(selectedId);
 if(!associated)reasons.push('NO_MATCHING_DOSSIER');
 let documented=0,divergences=0,missing=[...REQUIRED_DOMAINS];
 if(associated){
  const provenance=auditEvidenceProvenance(dossier);
  const classification=classifyEvidence(dossier);
  documented=provenance.documented_count;
  divergences=classification.contradictions.length;
  missing=evidence.missing_domains;
  if(documented<provenance.entries.length)reasons.push('INCOMPLETE_PROVENANCE');
  if(divergences>0)reasons.push('DOCUMENTARY_DIVERGENCES');
  if(missing.length>0)reasons.push('MISSING_DECLARED_VERIFIED_DOMAINS');
 }
 reasons.push('NO_INDEPENDENT_SOURCE_VERIFICATION','KRAFT_EXECUTION_NOT_IMPLEMENTED');
 return {
  schema:'BET_ANALYST_GLOBAL_DIAGNOSTIC_V1',match_id:selected?String(selectedId):null,
  snapshot_usable:match.usable,snapshot_freshness:match.freshness,
  dossier_valid:evidence.valid,associated,
  documented_count:documented,documentary_divergences:divergences,
  missing_domains:missing,reasons:[...new Set(reasons)],
  independent_verification_count:0,analysis_readiness:'BLOCKED',
  scope:'Contrôles techniques et documentaires uniquement. C1/C2/C3 méthodologiques non exécutés.'
 };
}
