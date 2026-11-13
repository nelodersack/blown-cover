// Spielt die protokollierten Schreibvorgänge (dev/harness.py, WLOG) gegen database.rules.json ab (targaryen, ohne Emulator)
const t=require('targaryen'),fs=require('fs'),path=require('path');
const [,, rulesFile, dir]=process.argv;const rules=JSON.parse(fs.readFileSync(rulesFile,'utf8'));
const clean=o=>{if(o===null||typeof o!=='object')return o;const r={};for(const k in o){if(k.startsWith('.'))continue;const v=clean(o[k]);if(v!==null&&v!==undefined&&!(typeof v==='object'&&!Object.keys(v).length))r[k]=v}return r};
const seen=new Map();let n=0,bad=0;
for(const f of fs.readdirSync(dir).sort()){const W=JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));const test=f.replace(/_\d+\.json$/,'');
  for(const w of W){n++;const before=clean(JSON.parse(w.before));const p='/'+w.p.replace(/^\/+/,'');
    if(p.startsWith('/.info'))continue;
    let res;try{const db=t.database(rules,before,w.now).as(w.uid?{uid:w.uid}:null);
      res=w.op==='update'?db.update(p,clean(w.v)===undefined?{}:w.v,{now:w.now}):db.write(p,w.v,{now:w.now})}catch(e){res={allowed:false,info:'EXC '+e.message}}
    if(!res.allowed){bad++;const key=test+' | '+w.op+' '+p.replace(/u\d+|[A-Za-z0-9]{20,}/g,'$U')+' | '+(w.op==='update'?Object.keys(w.v).map(k=>k.replace(/u\d+/g,'$U')).sort().join(','):typeof w.v==='object'&&w.v?Object.keys(w.v).sort().join(','):JSON.stringify(w.v));
      if(!seen.has(key))seen.set(key,{c:0,w,info:res.info});seen.get(key).c++}}}
console.log('Schreibvorgänge der App in den Tests:',n,'· von den Regeln abgelehnt:',bad);process.on('exit',()=>{process.exitCode=bad?1:0});
for(const [k,v] of seen){console.log('\n### '+k+'  ×'+v.c+'  uid='+v.w.uid);console.log('  Wert:',JSON.stringify(v.w.v).slice(0,300));
  if(process.env.INFO)console.log(String(v.info).split('\n').filter(l=>/=> false|No \.write|\.validate|EXC/.test(l)).slice(0,6).join('\n'))}
