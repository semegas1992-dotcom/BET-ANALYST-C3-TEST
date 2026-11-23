// C3.13-A — audit documentaire de provenance, sans certification externe.
import {validateKraftEvidence} from './c3-11-kraft-evidence.js';
const nonempty=v=>typeof v==='string'&&v.trim().length>0;
const iso=v=>nonempty(v)&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(v)&&Number.isFinite(Date.parse(v));
export function auditEvidenceProvenance(dossier){
 const structure=validateKraftEvidence(dossier);
 const items=Array.isArray(dossier?.evidence)?dossier.evidence:[];
 const entries=items.map((e,i)=>{
  const source=nonempty(e?.source)?e.source.trim():null;
  const observed_at=iso(e?.observed_at)?e.observed_at:null;
  const verification_note=nonempty(e?.verification_note)?e.verification_note.trim():null;
  const state=typeof e?.state==='string'?e.state:'INVALID';
  const flags=[];
  if(!source)flags.push('SOURCE_NOT_DOCUMENTED');
  if(!observed_at)flags.push('OBSERVATION_DATE_NOT_DOCUMENTED');
  if(state==='VERIFIED'&&!verification_note)flags.push('VERIFICATION_NOTE_NOT_DOCUMENTED');
  if(observed_at&&iso(dossier?.created_at)&&Date.parse(observed_at)>Date.parse(dossier.created_at))flags.push('OBSERVATION_AFTER_DOSSIER_CREATION');
  return {
   index:i,id:nonempty(e?.id)?e.id:null,domain:nonempty(e?.domain)?e.domain:null,
   declared_state:state,declared_source:source,declared_observed_at:observed_at,
   declared_verification_note:verification_note,flags,
   documentation_complete:flags.length===0,
   independently_verified:false
  };
 });
 return {
  schema:'BET_ANALYST_PROVENANCE_AUDIT_V1',
  dossier_valid:structure.valid,
  errors:structure.errors,
  match_id:nonempty(dossier?.match_id)?dossier.match_id:null,
  entries,
  documented_count:entries.filter(e=>e.documentation_complete).length,
  independent_verification_count:0,
  analysis_readiness:'BLOCKED',
  limitation:'Les sources, dates et vérifications sont déclarées dans le fichier ; aucune authentification externe.'
 };
}
