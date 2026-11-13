# Test: Zombie-Modus und Teams auslosen (Lobby, Auslosen beim Start, Verwandlung mit Wartezeit, Ping-Intervall, Letzter Überlebender, Endscreen, Replay)
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:500,rMin:300,shrink:5,step:50,head:2,dur:60,ping:120,pen:2,mode:'zombie',taskR:0,imm:240,shOn:false,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:20,hbL:60,hbT:30,gw:20,gd:60,ot:5,rp:true,rnd:true,rH:1}"
PL="""u1:{name:'Anna',role:'hider',state:'alive',j:1,col:0,lat:47.0725,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},
  u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.4430,ts:T},u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0680,lng:15.4380,ts:T},
  u5:{name:'Ben',role:'hider',state:'alive',j:5,col:4,lat:47.0675,lng:15.4370,ts:T}"""
TO="window.__toasts=[];const _t=toast;window.toast=m=>{__toasts.push(String(m));return _t(m)}"
def shot(pg,n):pg.screenshot(path=OUT+'/zombie_'+n+'.png')
def lobby(ev,me):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',rn:0,c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5'}}};
      uid='%s';pos={lat:__T.games.K7QF.players['%s'].lat,lng:__T.games.K7QF.players['%s'].lng};lastFix=Date.now()})()"""%(S,PL,me,me,me))
    ev("join('K7QF')")
def tick(ev):ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)")

# 1 Lobby + Auslosen beim Start
with app(390,844) as (pg,ev,errs):
    lobby(ev,'u1');pg.wait_for_timeout(900);tick(ev);ev(TO)
    t=ev("document.getElementById('pb').innerText");print(t[:400].replace('\n',' | '))
    assert 'werden ausgelost' in t and '1 Zombie' in t and 'Anzahl Zombies' in t and 'Patient Null' in t
    shot(pg,'lobby_spieler')
    ev("tabGo('lt','set')");ev("ui.open.tasks=1;panel(1)");pg.wait_for_timeout(300);shot(pg,'lobby_modus')
    ev("ui.open.zmb=1;panel(1)");pg.wait_for_timeout(300)
    z=ev("document.getElementById('pb').textContent");assert 'Verwandlungszeit' in z and 'Verwandlungsradius' in z and 'Ping-Deckel' in z,z[:500]
    ev("setS('zC',2.5,1.5,5);setS('zR',40,20,100);setS('zT',30,10,600)");pg.wait_for_timeout(300)
    assert ev("G.s.zC")==2.5 and ev("G.s.zR")==40 and ev("G.s.zT")==30
    ev("stp('zC',-1)");pg.wait_for_timeout(300);assert ev("G.s.zC")==2.0,ev("G.s.zC")
    shot(pg,'lobby_zombie_menue')
    ev("setS('zC',3,1.5,5);setS('zR',30,20,100);setS('zT',20,10,600)");pg.wait_for_timeout(300)
    assert 'zombie' in ev("document.getElementById('pb').textContent").lower()
    ev("window.mkPts=async(c,R,n)=>randPts(c,R,n,30,[]);window.chkGps=async()=>[]")
    ev("st()");pg.wait_for_timeout(2500)
    print('status',ev("G.status"),ev("JSON.stringify(Object.values(G.players).map(p=>p.role))"))
    assert ev("G.status")=='running' and ev("Object.values(G.players).filter(p=>p.role==='hunter').length")==1
    pg.wait_for_timeout(600);shot(pg,'briefing_rolle')
    print(ev("(document.getElementById('bfd')||{}).textContent||''")[:300]);assert 'Ausgelost' in ev("(document.getElementById('bfd')||{}).textContent||''")
    assert not [e for e in errs if 'PE:' in e],errs

# 2 Verwandlung: Lena (u2) wird von Anna gefangen
def running(ev,me,el=600,extra=''):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',rn:0,startAt:T-120000-%d*1000,c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5'}}};
      const g=__T.games.K7QF;g.players.u1.role='hunter';g.players.u1.lat=47.07055;g.players.u1.lng=15.4405;%s
      uid='%s';pos={lat:g.players['%s'].lat,lng:g.players['%s'].lng};lastFix=Date.now()})()"""%(el,S,PL,extra,me,me,me))
    ev("join('K7QF')");pg.wait_for_timeout(1300);ev("typeof bfClose==='function'&&bfClose()")
with app(390,844) as (pg,ev,errs):
    running(ev,'u2');tick(ev);ev(TO)
    ev("__T.games.K7QF.catches={u2:{hunter:'u1',t:Date.now()-3000,status:'pending',lat:47.0705,lng:15.4405}};notify()");pg.wait_for_timeout(800)
    ev("ok()");pg.wait_for_timeout(1200)
    me=ev("JSON.stringify(G.players.u2)");print(me);m=ev("G.players.u2")
    assert m['role']=='hunter' and m['zt'] and m['zb']=='u1' and m['zl'] and m['state']=='alive'
    assert 'infiziert' in ev("JSON.stringify(G.ev)")
    pg.wait_for_timeout(1200);t=ev("document.getElementById('pb').innerText");print(t[:300].replace('\n',' | '))
    assert ev("!!document.querySelector('.card.zv')") and ev("zLock(G,uid)")
    ev("map.setView([47.0703,15.4405],18,{animate:false});draw()");pg.wait_for_timeout(500);shot(pg,'verwandlung')
    ev("cc()");assert 'Verwandlung' in ev("__toasts.slice(-1)[0]"),ev("__toasts")
    # Kreis verlassen -> zurückgesetzt
    ev("pos={lat:47.0712,lng:15.4405};lastFix=Date.now()");pg.wait_for_timeout(1600)
    print(ev("__toasts.slice(-2)"),ev("JSON.stringify(ZV)"));assert ev("ZV.ph")=='out'
    ev("map.setView([47.0707,15.4405],18,{animate:false});draw()");pg.wait_for_timeout(500);shot(pg,'verwandlung_raus')
    ev("pos={lat:47.0705,lng:15.4405};lastFix=Date.now()");pg.wait_for_timeout(1500);assert ev("ZV.ph")=='in'
    ev("ZV.st-=60000");pg.wait_for_timeout(1800)
    print('zd',ev("G.players.u2.zd"));assert ev("G.players.u2.zd") and not ev("zLock(G,uid)")
    pg.wait_for_timeout(800);shot(pg,'zombie_jagt')
    assert not [e for e in errs if 'PE:' in e],errs

# 3 Ping-Intervall, Letzter Überlebender, Endscreen, Replay
with app(390,844) as (pg,ev,errs):
    T0="Date.now()-720000"
    running(ev,'u1',600,"g.players.u2.role='hunter';g.players.u2.zt=Date.now()-300000;g.players.u2.zb='u1';g.players.u2.zd=Date.now()-280000;g.players.u3.role='hunter';g.players.u3.zt=Date.now()-200000;g.players.u3.zb='u2';g.players.u3.zd=Date.now()-180000;g.players.u4.role='hunter';g.players.u4.zt=Date.now()-100000;g.players.u4.zb='u2';g.players.u4.zd=Date.now()-80000;")
    tick(ev);ev(TO)
    iv=ev("zIv(G,P(),now())");print('Ping-Intervall',iv);assert iv==360000   # 4 Zombies/1 Hider vs 1/4: √16=4 -> max 3·p0
    iv0=ev("zIv(G,P(),G.startAt+2*6e4+1000)");assert iv0==120000
    assert ev("(()=>{G.s.zC=2;const v=zIv(G,P(),now());G.s.zC=3;return v})()")==240000
    assert ev("(()=>{G.s.zP=false;const v=zIv(G,P(),now());delete G.s.zP;return v})()")==120000
    pg.wait_for_timeout(1500);print(ev("JSON.stringify(G.ev)"));assert 'Letzter Überlebender: Ben' in ev("JSON.stringify(G.ev)")
    shot(pg,'zombie_karte');ev("lgToggle()");pg.wait_for_timeout(300);shot(pg,'legende')
    assert 'Verwandelt' in ev("document.getElementById('lg').innerText")
    ev("lgToggle()")
    # Endscreen
    ev("__T.games.K7QF.players.u5.state='caught';__T.games.K7QF.players.u5.role='hunter';__T.games.K7QF.players.u5.state='alive';__T.games.K7QF.players.u5.zt=Date.now()-1000;__T.games.K7QF.players.u5.zb='u4';__T.games.K7QF.status='over';__T.games.K7QF.winner='hunter';notify()")
    pg.wait_for_timeout(1500);t=ev("document.body.innerText");print(t[:900].replace('\n',' | '))
    t=ev("document.getElementById('res').textContent");assert 'Zombies gewinnen' in t and 'Meiste Infektionen' in t and 'Lena2' in t.replace(' ','').replace('×','')
    shot(pg,'endscreen')
    # Replay: Rollenwechsel über die Zeit
    f=ev("(()=>{const f=rpBuild();return JSON.stringify(f.players.map(p=>[p.name,p.role,!!p.zt,p.zb]))})()");print(f)
    ev("rvLoad(rpBuild())");pg.wait_for_timeout(800)
    r=ev("(()=>{const p=Object.values(RV.pl).find(p=>p.name==='Max');return [rvRole(p,p.zt-1000),rvRole(p,p.zt+1000)]})()");print(r);assert r==['hider','hunter']
    assert ev("RV.f.players.some(p=>p.zt)")
    ev("rvJump(Object.values(RV.pl).find(p=>p.name==='Tom').zt+2000)");pg.wait_for_timeout(800);shot(pg,'replay')
    evs=ev("JSON.stringify((RV.ev||[]).filter(e=>/infiziert/.test(e.x)).map(e=>e.x))");print(evs)
    assert not [e for e in errs if 'PE:' in e],errs
print('ok')
