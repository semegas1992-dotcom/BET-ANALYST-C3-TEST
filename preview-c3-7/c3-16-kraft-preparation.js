// C3.16-A — pré-analyse structurée, non moteur KRAFT V3.0.
// Aucune projection, probabilité, cote ou scénario sportif inventé.
import {validateKraftEvidence,REQUIRED_DOMAINS} from './c3-11-kraft-evidence.js';
const STATES=['VERIFIED','UNVERIFIED','HYPOTHESIS','MISSING'];
export function prepareKraftInput(dossier){
 const audit=validateKraftEvidence(dossier);
 const domains=REQUIRED_DOMAINS.map(domain=>{
  const items=audit.valid?dossier.evidence.filter(e=>e.domain===domain):[];
  return {domain,items:items.map(e=>({
   id:e.id,state:e.state,value:e.value,
   source:typeof e.source==='string'?e.source:null,
   observed_at:typeof e.observed_at==='string'?e.observed_at:null,
   rationale:typeof e.rationale==='string'?e.rationale:null
  })),counts:Object.fromEntries(STATES.map(s=>[s,items.filter(e=>e.state===s).length]))};
 });
 return {schema:'BET_ANALYST_KRAFT_PREPARATION_V1',valid:audit.valid,errors:audit.errors,
  match_id:audit.valid?dossier.match_id:null,domains,
  sections:[
   {key:'FACTS',label:'Faits déclarés',item_ids:audit.valid?dossier.evidence.filter(e=>e.state==='VERIFIED').map(e=>e.id):[]},
   {key:'UNVERIFIED',label:'Informations non vérifiées',item_ids:audit.valid?dossier.evidence.filter(e=>e.state==='UNVERIFIED').map(e=>e.id):[]},
   {key:'HYPOTHESES',label:'Hypothèses',item_ids:audit.valid?dossier.evidence.filter(e=>e.state==='HYPOTHESIS').map(e=>e.id):[]},
   {key:'MISSING',label:'Informations manquantes',item_ids:audit.valid?dossier.evidence.filter(e=>e.state==='MISSING').map(e=>e.id):[]}
  ],
  rapport_de_force:{status:'NOT_COMPUTED',reason:'Absence de moteur sportif et de données indépendamment vérifiées'},
  scenarios:['A','B','C'].map(id=>({id,status:'NOT_COMPUTED',description:null})),
  markets:{status:'NOT_EVALUATED',candidates:[]},
  probabilities:{status:'NOT_COMPUTED'},
  analysis_readiness:'BLOCKED',independently_verified:false,
  disclaimer:'Préparation documentaire uniquement : ne constitue pas une analyse KRAFT V3.0.'};
}
