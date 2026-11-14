// Handgebaute Fälle für Regeln, die die App-Tests nicht abdecken
const t=require('targaryen'),fs=require('fs');const rules=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const N=1794600000000;
const base=(over)=>{const g={host:'u1',status:'running',rn:0,startAt:N-600000,c:{lat:47.07,lng:15.44},
  s:{r0:500,rMin:300,shrink:5,step:50,head:2,dur:60,ping:120,pen:2,mode:'zombie',imm:120,hbC:20,rnd:true,rH:1,fs:true,fsT:40,fsR:40},
  players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:N-1000},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.07,lng:15.44,ts:N-1000,immUntil:N+5000},
    u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.071,lng:15.44,ts:N-1000},u4:{name:'Tom',role:'hunter',state:'alive',j:4,col:3,lat:47.07,lng:15.44,ts:N-1000}},
  catches:{u2:{hunter:'u1',t:N-31000,status:'pending',lat:47.07,lng:15.44}},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}};
  return {games:{K7QF:Object.assign(g,over||{})}}};
const zInf=(h,hu)=>({[`players/${h}/role`]:'hunter',[`players/${h}/zt`]:N,[`players/${h}/zs`]:N,[`players/${h}/zb`]:hu,[`players/${h}/sT`]:N,[`players/${h}/immUntil`]:null,[`players/${h}/revealUntil`]:null,[`players/${h}/out`]:null,[`players/${h}/zl`]:{lat:47.07,lng:15.44},[`ev/${h}_c`]:{t:N,x:'Lena wurde von Anna infiziert',u:h},[`catches/${h}/status`]:'done'});
let fail=0;const T=(name,want,data,uid,op,p,v)=>{const db=t.database(rules,data,N).as(uid?{uid}:null);const r=op==='update'?db.update(p,v,{now:N}):op==='read'?db.read(p,{now:N}):db.write(p,v,{now:N});
  const ok=r.allowed===want;if(!ok)fail++;console.log((ok?'ok  ':'FALSCH ')+name+' → '+(r.allowed?'erlaubt':'abgelehnt')+(ok?'':'\n'+String(r.info).split('\n').filter(l=>/=> false|No \.write|validate/.test(l)).slice(0,8).join('\n')))};
const G='/games/K7QF';
T('Zombie: Infektion durch Fänger nach Timeout',true,base(),'u1','update',G,zInf('u2','u1'));
T('Zombie: Infektion durch den Hider selbst (ok)',true,base(),'u2','update',G,zInf('u2','u1'));
T('Zombie: Infektion durch fremden Hunter',false,base(),'u4','update',G,zInf('u2','u1'));
T('Zombie: Infektion ohne offene Fangmeldung',false,base(),'u1','update',G,zInf('u3','u1'));
T('Kein Zombie-Modus: Rollenwechsel',false,(()=>{const d=base();d.games.K7QF.s.mode='survive';return d})(),'u2','update',G,zInf('u2','u1'));
T('Zombie: Hunter macht sich selbst zum Hider',false,base(),'u1','set',G+'/players/u1/role','hider');
T('Zombie: Verwandlung fertig (zd)',true,(()=>{const d=base();Object.assign(d.games.K7QF.players.u2,{role:'hunter',zt:N-30000});return d})(),'u2','set',G+'/players/u2/zd',N);
T('Zombie: zd durch anderen',false,(()=>{const d=base();Object.assign(d.games.K7QF.players.u2,{role:'hunter',zt:N-30000});return d})(),'u1','set',G+'/players/u2/zd',N);
T('Verwandelter Zombie meldet Fang',true,(()=>{const d=base();Object.assign(d.games.K7QF.players.u2,{role:'hunter',zt:N-30000,zd:N-5000});d.games.K7QF.catches.u2.status='done';return d})(),'u2','set',G+'/catches/u3',{hunter:'u2',t:N,status:'pending',lat:47.07,lng:15.44});
// Neue Runde nach Zombie-Spiel
{const d=base({status:'over',winner:'hunter',fz:{u3:{h:'u1',t:N-100000}}});Object.assign(d.games.K7QF.players.u2,{role:'hunter',zt:N-30000,zb:'u1',zs:N-30000,zl:{lat:47,lng:15},zd:N-1000,sT:N-30000});d.games.K7QF.catches.u2.status='done';
 const u={status:'lobby',startAt:null,winner:null,tasks:null,catches:null,hb:null,live:null,xp:null,ev:null,fz:null,rn:1,prev:{j:'{}'}};
 for(const k of ['u1','u2','u3','u4']){const p=d.games.K7QF.players[k];u['players/'+k]=Object.assign({name:p.name,role:p.zt?'hider':p.role,state:'alive',j:p.j,col:p.col},k==='u1'?{}:{w:true})}
 T('Neue Runde nach Zombie (Host)',true,d,'u1','update',G,u);T('Neue Runde nach Zombie (Mitspieler)',true,d,'u3','update',G,Object.assign({},u,{['players/u3']:{name:'Max',role:'hider',state:'alive',j:3,col:2},['players/u1']:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,w:true}}))}
// Auslosen beim Start
{const d=base({status:'lobby',startAt:null,catches:null});for(const k in d.games.K7QF.players)d.games.K7QF.players[k].role='hider';
 const u={status:'running',startAt:N+5000,'players/u1/role':'hider','players/u2/role':'hunter','players/u3/role':'hider','players/u4/role':'hider'};
 T('Auslosen: Host schreibt Rollen beim Start',true,d,'u1','update',G,u);T('Auslosen: Nicht-Host schreibt Rollen',false,d,'u2','update',G,u);
 d.games.K7QF.s.rnd=false;T('Ohne Auslosen: Host schreibt fremde Rolle',false,d,'u1','set',G+'/players/u2/role','hunter')}
// Fang starten
T('Fang starten: Hunter löst aus',true,base(),'u1','set',G+'/fz/u3',{h:'u1',t:N});
T('Fang starten: Hider löst aus',false,base(),'u3','set',G+'/fz/u2',{h:'u3',t:N});
T('Fang starten: fremde Hunter-ID',false,base(),'u1','set',G+'/fz/u3',{h:'u4',t:N});
T('Fang starten: auf Hunter',false,base(),'u1','set',G+'/fz/u4',{h:'u1',t:N});
T('Fang starten: läuft schon',false,base({fz:{u3:{h:'u4',t:N-10000}}}),'u1','set',G+'/fz/u3',{h:'u1',t:N});
T('Fang starten: alter Countdown abgelaufen',true,base({fz:{u3:{h:'u4',t:N-41000}}}),'u1','set',G+'/fz/u3',{h:'u1',t:N});
T('Fang starten: Schalter aus',false,(()=>{const d=base();d.games.K7QF.s.fs=false;return d})(),'u1','set',G+'/fz/u3',{h:'u1',t:N});
T('Fang starten: Ergebnis schreibt Hider',true,base(),'u3','set','/fzp/K7QF/u3',{t:N,ok:true});
T('Fang starten: Hunter liest Ergebnis',false,(()=>{const d=base();d.fzp={K7QF:{u3:{t:N,ok:true}}};return d})(),'u1','read','/fzp/K7QF/u3');
T('Fang starten: Hunter liest ganzen fzp-Knoten',false,(()=>{const d=base();d.fzp={K7QF:{u3:{t:N,ok:true}}};return d})(),'u1','read','/fzp/K7QF');
T('Fang starten: Hider liest eigenes Ergebnis',true,(()=>{const d=base();d.fzp={K7QF:{u3:{t:N,ok:true}}};return d})(),'u3','read','/fzp/K7QF/u3');
T('Entkommen: Hider setzt Schutz + Ping-Ausfall',true,base(),'u3','update',G+'/players/u3',{immUntil:N+60000,pS:N+90000});
T('Ping-Ausfall durch anderen',false,base(),'u1','set',G+'/players/u3/pS',N+90000);
// Kick, Host
{const d=base({status:'lobby',startAt:null,catches:null});
 T('Host entfernt Spieler',true,d,'u1','update',G,{'players/u3':null,'cols/2':null});T('Nicht-Host entfernt Spieler',false,d,'u2','update',G,{'players/u3':null,'cols/2':null});
 T('Host-Übernahme, Host 79 s still',false,(()=>{const x=JSON.parse(JSON.stringify(d));x.games.K7QF.players.u1.ts=N-79000;return x})(),'u2','set',G+'/host','u2');
 T('Host-Übernahme, Host 81 s still',true,(()=>{const x=JSON.parse(JSON.stringify(d));x.games.K7QF.players.u1.ts=N-81000;return x})(),'u2','set',G+'/host','u2')}
// Neues Spiel mit den Standardwerten (preOf(60) = Balancing für 2 Hunter/4 Hider)
T('Neues Spiel anlegen',true,{},'u9','set','/games/N3WG',{host:'u9',status:'lobby',c:{lat:47.07,lng:15.44},s:{mode:'survive',taskR:0,shOn:true,bon:true,hbOn:true,hbN:2,gw:20,gd:60,dur:60,pen:2,shT:20,ddT:8,mtT:15,evT:8,hbT:30,ot:5,r0:900,rMin:400,shrink:4,step:55,head:5,ping:290,imm:290,hbC:150,hbL:70,ddN:1,mtN:1}});
// Einstellungen
{const d=base({status:'lobby',startAt:null,catches:null});const S=(k,v,w)=>T('Einstellung '+k+'='+v,w,d,'u1','set',G+'/s/'+k,v);
 S('zT',60,true);S('zR',30,true);S('zC',2.5,true);S('zP',false,true);S('zB',false,true);S('fs',true,true);S('fsR',40,true);S('fsT',40,true);S('rnd',true,true);S('rH',2,true);S('mode','zombie',true);S('zC',9,false);S('mode','x',false);
 T('Einstellung durch Nicht-Host',false,d,'u2','set',G+'/s/zT',60)}
console.log(fail?"\n"+fail+" FALSCH":"\nalle Fälle wie erwartet");process.exit(fail?1:0);
