// C3.13-C — classification conservatrice et détection de contradictions documentaires.
// Aucune inférence sportive, aucun appel réseau, aucune validation indépendante.
import {validateKraftEvidence,REQUIRED_DOMAINS} from './c3-11-kraft-evidence.js';
import {auditEvidenceProvenance} from './c3-13-provenance.js';
const stable=v=>typeof v==='string'?v.trim():String(v);
export function classifyEvidence(dossier){
 const audit=validateKraftEvidence(dossier);
 const provenance=auditEvidenceProvenance(dossier);
 if(!audit.valid)return {valid:false,errors:audit.errors,domains:[],contradictions:[],analysis_readiness:'BLOCKED'};
 const domains=REQUIRED_DOMAINS.map(domain=>{
  const entries=dossier.evidence.filter(e=>e.domain===domain);
  const documented=entries.filter(e=>provenance.entries.find(p=>p.id===e.id)?.documentation_complete).length;
  const counts={VERIFIED:0,UNVERIFIED:0,HYPOTHESIS:0,MISSING:0};
  for(const e of entries)counts[e.state]++;
  return {domain,total:entries.length,documented,counts,has_conflict:false};
 });
 const contradictions=[];
 // Seules les valeurs contradictoires dans un même domaine sont signalées.
 // Il s'agit de divergences textuelles, pas de contradictions sportives démontrées.
 for(const domain of REQUIRED_DOMAINS){
  const entries=dossier.evidence.filter(e=>e.domain===domain&&e.state==='VERIFIED');
  const values=new Map();
  for(const e of entries){const value=stable(e.value);if(!values.has(value))values.set(value,[]);values.get(value).push(e.id)}
  if(values.size>1){
   contradictions.push({domain,kind:'DIVERGENT_DECLARED_VERIFIED_VALUES',evidence_ids:entries.map(e=>e.id)});
   domains.find(d=>d.domain===domain).has_conflict=true;
  }
 }
 return {valid:true,errors:[],domains,contradictions,analysis_readiness:'BLOCKED',independently_verified:false,
  limitation:'La divergence des valeurs est un signal documentaire ; elle ne prouve pas une contradiction sportive.'};
}
