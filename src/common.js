const $=id=>document.getElementById(id);
const eur=v=>isFinite(v)?v.toLocaleString('it-IT',{style:'currency',currency:'EUR'}):'–';
const eur0=v=>isFinite(v)?v.toLocaleString('it-IT',{style:'currency',currency:'EUR',maximumFractionDigits:0}):'–';
const num=(v,d=2)=>isFinite(v)?v.toLocaleString('it-IT',{maximumFractionDigits:d,minimumFractionDigits:0}):'–';
const val=id=>{const x=parseFloat(String($(id).value).replace(',','.'));return isNaN(x)?0:x};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const on=(ids,fn)=>ids.forEach(i=>{const e=$(i);if(e){e.addEventListener('input',fn);e.addEventListener('change',fn)}});
const qs=s=>encodeURIComponent(s.trim().replace(/\s+/g,' '));
function parsePrices(txt){return String(txt).split(/[\s;]+/).map(s=>s.replace(/[€]/g,'').replace(/\.(?=\d{3}(\D|$))/g,'').replace(',','.')).map(parseFloat).filter(x=>isFinite(x)&&x>0)}
function priceStats(arr){
  if(!arr.length)return null;
  const s=[...arr].sort((a,b)=>a-b),med=a=>a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2;
  const m0=med(s),clean=s.filter(x=>x>=m0*0.5&&x<=m0*2),m=med(clean),avg=clean.reduce((t,x)=>t+x,0)/clean.length;
  return {n:s.length,used:clean.length,min:clean[0],max:clean[clean.length-1],avg,med:m,fast:m*0.85};
}
function lk(L){return L.map(([u,t,s])=>`<a href="${u}" target="_blank" rel="noopener nofollow" style="border:1px solid var(--line)"><span>${t}<small>${esc(s)}</small></span><span class="arr">↗</span></a>`).join('')}
