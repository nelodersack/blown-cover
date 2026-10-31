window.__T={};window.__ls=[];
const getp=(p)=>{let o=__T;for(const k of p.split('/').filter(Boolean)){if(o==null||typeof o!=='object')return null;o=o[k]}return o===undefined?null:o};
const setp=(p,v)=>{const ks=p.split('/').filter(Boolean);let o=__T;for(let i=0;i<ks.length-1;i++){if(o[ks[i]]==null||typeof o[ks[i]]!=='object')o[ks[i]]={};o=o[ks[i]]}
 const l=ks[ks.length-1];if(v===null||v===undefined)delete o[l];else o[l]=JSON.parse(JSON.stringify(v));
 // leere Knoten entfernen
 for(let n=ks.length-1;n>0;n--){const par=getp(ks.slice(0,n).join('/'));if(par&&typeof par==='object'&&!Object.keys(par).length)setp0(ks.slice(0,n).join('/'));else break}};
const setp0=p=>{const ks=p.split('/').filter(Boolean);let o=__T;for(let i=0;i<ks.length-1;i++)o=o[ks[i]];delete o[ks[ks.length-1]]};
const snap=v=>({val:()=>v==null?null:JSON.parse(JSON.stringify(v)),exists:()=>v!=null,key:null});
const notify=()=>{__ls.slice().forEach(l=>{try{l.cb(snap(getp(l.p)))}catch(e){console.error('ls',e)}})};
const R=p=>({
 set(v){setp(p,v);setTimeout(notify,0);return Promise.resolve()},
 update(u){for(const [k,v] of Object.entries(u))setp(p+'/'+k,v);setTimeout(notify,0);return Promise.resolve()},
 remove(){setp(p,null);setTimeout(notify,0);return Promise.resolve()},
 get(){return Promise.resolve(snap(getp(p)))},once(){return Promise.resolve(snap(getp(p)))},
 on(e,cb){if(e==='value'){__ls.push({p,cb});setTimeout(()=>cb(snap(getp(p))),0)}return cb},
 off(){for(let i=__ls.length-1;i>=0;i--)if(__ls[i].p===p)__ls.splice(i,1)},
 child(c){return R(p+'/'+c)},limitToLast(){return {on(){},off(){}}},push(){return Promise.resolve()}});
window.firebase={initializeApp(){},database(){const f={ref:p=>R(p||'')};f.ServerValue={TIMESTAMP:1};return f},auth(){return{setPersistence(){return Promise.resolve()},signInAnonymously(){return new Promise(()=>{})}}}};
firebase.auth.Auth={Persistence:{SESSION:1}};
