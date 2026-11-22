// C3.5-D experimental secure backend. No deployment or real provider activation.
const JSON_HEADERS={'content-type':'application/json; charset=utf-8','cache-control':'no-store','access-control-allow-methods':'GET, OPTIONS','access-control-allow-headers':'content-type'};
function reply(data,status=200,origin=''){const headers={...JSON_HEADERS};if(origin)headers['access-control-allow-origin']=origin;return new Response(JSON.stringify(data),{status,headers})}
export default {
 async fetch(request,env){
  const allowed=env.ALLOWED_ORIGIN||'';
  const origin=request.headers.get('Origin')||'';
  const cors=!!allowed&&origin===allowed?allowed:'';
  if(origin&&!cors)return reply({status:'FORBIDDEN_ORIGIN'},403);
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{...JSON_HEADERS,...(cors?{'access-control-allow-origin':cors}:{})}});
  if(request.method!=='GET')return reply({status:'METHOD_NOT_ALLOWED'},405,cors);
  const url=new URL(request.url);
  if(url.pathname==='/health')return reply({status:'OK',provider_connected:false},200,cors);
  if(url.pathname!=='/v1/football/matches')return reply({status:'NOT_FOUND'},404,cors);
  if(!env.FOOTBALL_DATA_TOKEN)return reply({status:'NOT_CONFIGURED'},503,cors);
  if(env.PROVIDER_ENABLED!=='true')return reply({status:'PROVIDER_DISABLED'},503,cors);
  // Fail closed until a server-side rate-limit binding is configured. CORS alone is not access control.
  if(!env.RATE_LIMITER||typeof env.RATE_LIMITER.limit!=='function')return reply({status:'RATE_LIMIT_NOT_CONFIGURED'},503,cors);
  const code=url.searchParams.get('competition')||'';
  if(!/^[A-Z0-9]{2,8}$/.test(code))return reply({status:'INVALID_COMPETITION'},400,cors);
  // Explicit allowlist: never accept arbitrary URLs or pass-through paths.
  const competitions=(env.ALLOWED_COMPETITIONS||'').split(',').map(x=>x.trim()).filter(Boolean);
  if(!competitions.includes(code))return reply({status:'COMPETITION_NOT_ALLOWED'},403,cors);
  // Cache binding is mandatory: avoid repeated upstream requests for the same competition.
  if(!env.MATCH_CACHE||typeof env.MATCH_CACHE.get!=='function'||typeof env.MATCH_CACHE.put!=='function')return reply({status:'CACHE_NOT_CONFIGURED'},503,cors);
  const cacheKey='football-data:matches:'+code;
  try{
   const cached=await env.MATCH_CACHE.get(cacheKey,'json');
   if(cached&&cached.status==='RECEIVED_UNVERIFIED'&&cached.competition===code&&Array.isArray(cached.matches)&&typeof cached.retrieved_at==='string'){
    const age=Date.now()-Date.parse(cached.retrieved_at);
    if(Number.isFinite(age)&&age>=0&&age<300000)return reply({...cached,cache:'HIT'},200,cors);
   }
  }catch{return reply({status:'CACHE_UNAVAILABLE'},503,cors)}
  // One shared upstream quota across all competitions: never split the quota by competition.
  try{
   const decision=await env.RATE_LIMITER.limit({key:'football-data:global'});
   if(!decision||decision.success!==true)return reply({status:'RATE_LIMITED'},429,cors);
  }catch{return reply({status:'RATE_LIMIT_UNAVAILABLE'},503,cors)}
  try{
   const response=await fetch('https://api.football-data.org/v4/competitions/'+encodeURIComponent(code)+'/matches',{headers:{'X-Auth-Token':env.FOOTBALL_DATA_TOKEN},signal:AbortSignal.timeout(7000)});
   if(!response.ok)return reply({status:'PROVIDER_ERROR',http_status:response.status},502,cors);
   const raw=await response.json();
   const matches=Array.isArray(raw.matches)?raw.matches.slice(0,100).map(m=>({id:m.id||null,utcDate:m.utcDate||null,status:m.status||null,homeTeam:m.homeTeam&&m.homeTeam.name||null,awayTeam:m.awayTeam&&m.awayTeam.name||null,score:m.score&&m.score.fullTime||null})):[];
   const payload={status:'RECEIVED_UNVERIFIED',provider:'football-data.org',competition:code,retrieved_at:new Date().toISOString(),matches};
   try{await env.MATCH_CACHE.put(cacheKey,JSON.stringify(payload),{expirationTtl:300})}
   catch{return reply({status:'CACHE_WRITE_FAILED'},503,cors)}
   return reply({...payload,cache:'MISS'},200,cors);
  }catch{return reply({status:'PROVIDER_UNAVAILABLE'},502,cors)}
 }
};
