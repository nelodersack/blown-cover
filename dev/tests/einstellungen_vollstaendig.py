# Test: Jede Einstellung (FD und Schalter) ist in den Einstellungs-Unterseiten oder im Spieler-Reiter erreichbar (nichts geht beim Umbau verloren)
import sys,os,re;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
SW=['rnd','zP','zB','fs','tsol','shOn','bon','hbOn','an','dq','hp','rp','hk']
with app(390,844) as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();const s=Object.assign({mode:'zombie',taskR:0,shOn:true,bon:true,hbOn:true,hbN:2,gw:20,gd:60,hk:true,fs:true,dq:true,ot:5},preOf(60),hkDef(preOf(60)));
      __T.games={K7QF:{host:'u1',status:'lobby',rn:0,c:{lat:47.07,lng:15.44},s,players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.07,lng:15.44,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.07,lng:15.44,ts:T},u4:{name:'Ben',role:'hider',state:'alive',j:4,col:3,lat:47.07,lng:15.44,ts:T}},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}}};
      uid='u1';pos={lat:47.07,lng:15.44};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(800)
    seen=set();txt=''
    def grab():
        global txt
        h=ev("$('pb').innerHTML");txt+=h
        for m in re.finditer(r"(?:stp|edGo|setS|setB)\('(?:b:)?([A-Za-z0-9]+)'",h):seen.add(m.group(1))
        for k,f in [('hk','setHk('),('rnd','setRnd('),('mode','setMode(')]:
            if f in h:seen.add(k)
    ev("tabGo('lt','players')");pg.wait_for_timeout(200);grab()
    ev("setRnd(1)");pg.wait_for_timeout(400);grab()
    ev("tabGo('lt','set')");pg.wait_for_timeout(200);grab()
    for sp in ['zmb','bal','zone','game','tasks','bon','tech']:
        ev("subGo('%s')"%sp);pg.wait_for_timeout(250);grab()
        keys=ev("[...$('pb').querySelectorAll('button.mzc,button.mzi')].map(b=>(b.getAttribute('onclick').match(/edGo\\('([^']+)'/)||[])[1]).filter(Boolean)")
        for k in keys:
            ev("ui.ed=null;edGo('%s')"%k);pg.wait_for_timeout(120);grab()
    # Mission-Modus: Evakuierung und Belohnungs-Schalter
    ev("__T.games.K7QF.s.mode='mission';notify()");pg.wait_for_timeout(300)
    for sp in ['tasks','bon']:
        ev("subGo('%s')"%sp);pg.wait_for_timeout(250);grab()
        ev("ui.ed=null;edGo('evT')");pg.wait_for_timeout(120);grab()
    fd=ev("Object.keys(FD)")
    miss=[k for k in fd+SW if k not in seen]
    print('fehlt:',miss)
    assert not miss,miss
    print('errors:',[e for e in errs if 'PE:' in e])
    assert not [e for e in errs if 'PE:' in e]
