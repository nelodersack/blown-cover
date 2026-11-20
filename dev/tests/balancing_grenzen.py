# Test: feste Grenzen des Balancings (balCalc) für alle Modi, Besetzungen (1–10 Hunter, 1–20 Hider), Dauern und Reglerstufen.
# Diese Regeln stehen im Konzept (claude/KONZEPT_Balancing.md) und dürfen bei Formeländerungen nicht verloren gehen:
#  - mindestens 10 Pings pro Spiel (Ping ≤ Dauer · 6 s), Ping 30 s … 7 min (Zombie: Startping bis 15 min, wächst ohnehin)
#  - Mindestradius < Startradius, Mindestradius wird vor Spielende erreicht
#  - Headstart höchstens die halbe Dauer (Plausibilität)
#  - Immunität ≤ Ping (= Ping, nur durch das Feld-Maximum 10 min gedeckelt), Wartezeit nach Fang ≤ Ping
#  - Aufgaben: je 2 Hider eine (n = ⌊X/2⌋), Dead Drops + Meetings = n
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
CHK="""(()=>{const bad=[];let n=0;
 for(const mode of ['survive','mission','zombie'])for(const T of [20,30,45,60,90,120])for(let H=1;H<=10;H++)for(let X=1;X<=20;X++)for(let k=0;k<5;k++){
  n++;const s=Object.assign({},DEF,PRE[T]||PRE[30],{dur:T,mode}),r=balCalc(s,H,X,k),o=r.o,id=mode+' '+H+'/'+X+' '+T+'min k'+k,f=m=>bad.push(id+': '+m);
  if(!(o.ping<=T*6))f('nur '+(T*60/o.ping).toFixed(1)+' Pings (Ping '+o.ping+' s)');
  if(!(o.ping>=30&&o.ping<=(mode==='zombie'?900:420)))f('Ping '+o.ping);
  if(!(o.rMin<o.r0))f('rMin '+o.rMin+' ≥ r0 '+o.r0);
  if(!(Math.ceil((o.r0-o.rMin)/o.step)*o.shrink<=T))f('rMin erst nach '+Math.ceil((o.r0-o.rMin)/o.step)*o.shrink+' Min');
  if(!(o.head<=T/2))f('Headstart '+o.head);
  if(!(o.imm<=o.ping))f('Immunität > Ping');
  if(!(o.hbC<=o.ping))f('Wartezeit '+o.hbC+' > Ping');
  if(r.n!==Math.floor(X/2)||r.dd+r.mt!==r.n)f('Aufgaben '+JSON.stringify([r.n,r.dd,r.mt]));
 }
 const ty={};bad.forEach(b=>{const t=b.split(': ')[1].replace(/[0-9.]+/g,'#');ty[t]=(ty[t]||0)+1});return {n,bad:bad.length,ex:bad.filter((b,i)=>i%200==0).slice(0,14),ty}})()"""
with app() as (pg,ev,errs):
    pg.wait_for_timeout(300)
    r=ev(CHK);print('geprüft:',r['n'],'Verstöße:',r['bad']);[print('  ',x) for x in r['ex']];print(r['ty'])
    assert r['bad']==0
    print('errors:',errs[:8])
