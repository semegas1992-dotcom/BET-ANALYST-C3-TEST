// C3.12-A — liaison locale entre une rencontre et son dossier de preuves.
// Aucun appel réseau. Les identifiants ne sont pas une preuve de provenance.
import {validateSnapshot} from './c3-5-snapshot.js';
import {validateKraftEvidence} from './c3-11-kraft-evidence.js';

export function linkMatchEvidence(snapshot,dossier,options={}){
 const matchAudit=validateSnapshot(snapshot,options);
 const evidenceAudit=validateKraftEvidence(dossier);
 const errors=[];
 if(!matchAudit.usable)errors.push('MATCH_SNAPSHOT_INVALID');
 if(!evidenceAudit.valid)errors.push('EVIDENCE_DOSSIER_INVALID');
 const matchId=dossier&&typeof dossier.match_id==='string'?dossier.match_id:null;
 // L'identifiant du fournisseur est converti en chaîne décimale canonique.
 const matches=matchAudit.usable?matchAudit.matches:[];
 const matchesWithId=matches.filter(m=>String(m.id)===matchId);
 if(matchAudit.usable&&evidenceAudit.valid&&matchesWithId.length!==1)errors.push('MATCH_ID_NOT_FOUND');
 const linked=errors.length===0;
 return {
  linked,
  status:linked?'LINKED_UNVERIFIED':'REJECTED',
  errors,
  match:linked?{
   id:String(matchesWithId[0].id),
   home:matchesWithId[0].homeTeam,
   away:matchesWithId[0].awayTeam,
   date_utc:matchesWithId[0].utcDate
  }:null,
  evidence_count:linked?dossier.evidence.length:0,
  missing_domains:linked?evidenceAudit.missing_domains:[],
  analysis_readiness:'BLOCKED',
  verified:false
 };
}
