// C3.5-N — Read-only presentation model. No provider requests or sporting inference.
import {validateSnapshot} from './c3-5-snapshot.js';
export function buildMatchesView(snapshot,options={}){
 const audit=validateSnapshot(snapshot,options);
 if(!audit.usable)return {state:'UNAVAILABLE',message:'Données indisponibles ou invalides',matches:[],warnings:audit.errors,verified:false};
 const warnings=[];
 if(audit.freshness==='STALE')warnings.push('DONNEES_ANCIENNES');
 if(audit.truncated)warnings.push('LISTE_INCOMPLETE');
 const matches=audit.matches.map(m=>({
  id:m&&m.id!=null?String(m.id):null,
  date_utc:typeof m?.utcDate==='string'?m.utcDate:null,
  home:typeof m?.homeTeam==='string'&&m.homeTeam.trim()?m.homeTeam:null,
  away:typeof m?.awayTeam==='string'&&m.awayTeam.trim()?m.awayTeam:null,
  status:typeof m?.status==='string'?m.status:null,
  verified:false
 }));
 return {state:audit.freshness==='STALE'?'STALE':'READY',message:audit.freshness==='STALE'?'Instantané ancien — actualisation nécessaire':'Rencontres issues d’un instantané non vérifié',competition:audit.competition,retrieved_at:audit.retrieved_at,matches,warnings,verified:false};
}
