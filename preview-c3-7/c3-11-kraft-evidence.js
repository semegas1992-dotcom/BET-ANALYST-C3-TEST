// C3.11 — Dossier de preuves KRAFT expérimental. Aucun appel réseau ni analyse sportive.
// Les statuts documentent l'origine des éléments ; ils ne certifient jamais une vérité.
export const KRAFT_EVIDENCE_SCHEMA='BET_ANALYST_KRAFT_EVIDENCE_V1';
export const REQUIRED_DOMAINS=Object.freeze(['TEAM_FORM','TEAM_STATISTICS','SQUAD_AVAILABILITY','TACTICAL_CONTEXT','PLAYER_STATISTICS']);
const STATES=new Set(['VERIFIED','UNVERIFIED','HYPOTHESIS','MISSING']);
const OWN=Object.prototype.hasOwnProperty;
const nonempty=s=>typeof s==='string'&&s.trim().length>0;
const iso=s=>nonempty(s)&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s));
export function validateKraftEvidence(input){
 const errors=[];
 if(!input||typeof input!=='object'||Array.isArray(input))return {valid:false,errors:['INVALID_OBJECT'],analysis_readiness:'BLOCKED',missing_domains:[...REQUIRED_DOMAINS]};
 if(input.schema!==KRAFT_EVIDENCE_SCHEMA)errors.push('INVALID_SCHEMA');
 if(!nonempty(input.match_id))errors.push('INVALID_MATCH_ID');
 if(!iso(input.created_at))errors.push('INVALID_CREATED_AT');
 if(!Array.isArray(input.evidence))errors.push('INVALID_EVIDENCE');
 const evidence=Array.isArray(input.evidence)?input.evidence:[];
 const seen=new Set();
 for(let i=0;i<evidence.length;i++){
  const e=evidence[i];
  if(!e||typeof e!=='object'||Array.isArray(e)){errors.push('INVALID_ITEM_'+i);continue}
  if(!nonempty(e.id)||seen.has(e.id))errors.push('INVALID_OR_DUPLICATE_ID_'+i);
  else seen.add(e.id);
  if(!REQUIRED_DOMAINS.includes(e.domain))errors.push('INVALID_DOMAIN_'+i);
  if(!STATES.has(e.state))errors.push('INVALID_STATE_'+i);
  if(e.state==='MISSING'){
   if(e.value!==null)errors.push('MISSING_MUST_HAVE_NULL_VALUE_'+i);
  }else if(!OWN.call(e,'value')||e.value===null||typeof e.value==='object'||!['string','number','boolean'].includes(typeof e.value)||typeof e.value==='string'&&!e.value.trim())errors.push('INVALID_VALUE_'+i);
  if(e.state==='VERIFIED'){
   if(!nonempty(e.source)||!iso(e.observed_at)||!nonempty(e.verification_note))errors.push('VERIFICATION_EVIDENCE_REQUIRED_'+i);
  }
  if(e.state==='HYPOTHESIS'&&!nonempty(e.rationale))errors.push('HYPOTHESIS_RATIONALE_REQUIRED_'+i);
  if(e.state==='UNVERIFIED'&&nonempty(e.verification_note))errors.push('UNVERIFIED_CANNOT_CLAIM_VERIFICATION_'+i);
 }
 // Le dossier structure les preuves, mais aucune règle de suffisance sportive n'est définie ici.
 // Même un domaine renseigné ne suffit pas à autoriser automatiquement KRAFT.
 const missing_domains=REQUIRED_DOMAINS.filter(domain=>!evidence.some(e=>e?.domain===domain&&e.state==='VERIFIED'));
 return {valid:errors.length===0,errors,analysis_readiness:'BLOCKED',missing_domains,verified_count:evidence.filter(e=>e?.state==='VERIFIED').length};
}
