# Test: Radar (Hunter-Radar für Hider, Hider-Radar für Hunter), Satellitenbild, Meeting-Wahl, Dead-Drop-Dossier
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
S="{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:120,pen:2,mode:'survive',taskR:0,imm:120,shOn:false,shT:10,evT:5,ddN:1,ddT:0,mtN:1,mtT:0,bon:true,hbOn:true,hbN:2,hbC:0,hbL:60,hbT:1,gw:20,gd:60,ot:0}"
def setup(ev,me):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',rn:2,startAt:T-120000,c:{lat:47.07,lng:15.44},s:%s,
      tasks:{d1:{t0:T-60000,a:'u2',b:'u4',loc:{lat:47.071,lng:15.441},dep:{u:'u2',t:T-50000},pick:{u:'u4',t:T-40000}},
             m1:{t0:T-60000,a:'u2',b:'u3',loc:{lat:47.072,lng:15.442},fin:T-30000,p:{u2:{c:'bm',ok:true},u3:{c:'rad',ok:true}}}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0730,lng:15.4405,ts:T},u5:{name:'Ben',role:'hunter',state:'alive',j:5,col:4,lat:47.06,lng:15.43,ts:T},
        u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T},
        u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0600,lng:15.4300,ts:T}},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5'}}};
      uid='%s';pos={lat:G0.lat,lng:G0.lng};lastFix=Date.now()})()""".replace('G0',"__T.games.K7QF.players['%s']"%me)%(S,me))
    ev("join('K7QF')");ev("ui.tl=1");
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now();notify()},500)")
def mv(ev,u,dn):  # Spieler u dn Meter nördlich von Lena
    ev(f"__T.games.K7QF.players.{u}.lat=47.0705+{dn}/111320;__T.games.K7QF.players.{u}.lng=15.4405;notify()")
hud=lambda ev:ev("$('hud').innerText.replace(/\\n/g,' ')")
toasts=[]
# ---------- Hider
with app() as (pg,ev,errs):
    ev("window.__ts=[];const _t=toast;toast=(x,...r)=>{__ts.push(x);return _t(x,...r)}")
    setup(ev,'u2');pg.wait_for_timeout(1200);ev("bfClose()")
    its=ev("JSON.stringify(myItems(G))");print('Lena Items',its)
    tom=ev("JSON.stringify(myItems(G,'u4'))");print('Tom Items',tom)
    ta=ev("myItems(G).find(i=>i.id==='d1a').type");tb=ev("myItems(G,'u4').find(i=>i.id==='d1b').type")
    assert {ta,tb}=={'bm','radar'},(ta,tb)
    assert ev("ddBm({code:'K7QF',rn:2},'d1')")==ev("ddBm(G,'d1')")
    assert ev("myItems(G).find(i=>i.id==='m1m').type")=='bm'
    pb=ev("$('pb').innerText");print(pb.replace('\n',' | ')[:700])
    assert 'Hunter-Radar' in pb and 'Belohnung: Hunter-Radar' in pb and 'DEINE BONI' in pb.upper()
    # Bonus-Knopf öffnet Erklärung + Bestätigung, ohne gleich einzusetzen
    ev("document.querySelector('button.gb').click()");pg.wait_for_timeout(300)
    gd=ev("$('gd').innerText");print('Fenster:',gd.replace('\n',' | '));assert 'Jetzt einsetzen' in gd and 'Später' in gd
    assert not ev("(__T.games.K7QF.players.u2.used||{}).d1a"),'nicht ohne Bestätigung einsetzen'
    ev("[...$('gd').querySelectorAll('button')].find(b=>b.innerText==='Später').click()");pg.wait_for_timeout(200);assert not ev("!!$('gd')")
    assert 'Satellitenbild und Hunter-Radar' in ev("tkInfo(G.s,'d1',G.tasks.d1)[1]")
    assert 'Hunter-Radar oder Satellitenbild' in ev("tkInfo(G.s,'m1',G.tasks.m1)[1]")
    print('R/T auto',ev("[bmRv(G.s),bmTv(G.s)]"));assert ev("[bmRv(G.s),bmTv(G.s)]")==[100,120]
    mv(ev,'u1',300)
    ev("useBm('m1m')");pg.wait_for_timeout(1500);ev("$('panel').classList.add('c');map.setView([47.0705,15.4405],17,{animate:false})");pg.wait_for_timeout(600)
    print('HUD',hud(ev));assert 'Radar 0' in hud(ev)
    assert ev("!!document.querySelector('.leaflet-overlay-pane svg.bmr')") and not ev("document.querySelector('.leaflet-overlay-pane svg.bmr').classList.contains('hit')")
    shot(pg,'radar_such.png')
    mv(ev,'u1',60);pg.wait_for_timeout(1300)
    print('HUD',hud(ev));assert 'Radar 1' in hud(ev) and ev("document.querySelector('.leaflet-overlay-pane svg.bmr').classList.contains('hit')")
    mv(ev,'u5',90);pg.wait_for_timeout(1300);assert 'Radar 2' in hud(ev)
    shot(pg,'radar_kontakt.png')
    mv(ev,'u5',110);pg.wait_for_timeout(1300);print('Hysterese',hud(ev));assert 'Radar 2' in hud(ev)   # 110 m ≤ 100+15: bleibt drin
    mv(ev,'u5',130);pg.wait_for_timeout(1300);assert 'Radar 1' in hud(ev)
    mv(ev,'u1',300);pg.wait_for_timeout(1300);assert 'Radar 0' in hud(ev) and not ev("document.querySelector('.leaflet-overlay-pane svg.bmr').classList.contains('hit')")
    ts=ev("__ts.filter(x=>/Radar/.test(x))");print('Meldungen',ts)
    assert ts[0].startswith('Hunter-Radar aktiv') and any('2 Hunter' in x for x in ts) and ts[-1]=='Hunter-Radar: niemand mehr in der Nähe'
    # zweites Radar nicht gleichzeitig
    ev("__ts=[]");ev("useBm('d1a')");assert 'Dein Radar läuft noch' in ev("__ts")
    # Neuladen: Startzeit aus LS
    ev("BM.id=null");pg.wait_for_timeout(1200);assert 'Radar 0' in hud(ev)
    # Ablauf
    ev("LS[bmKey('m1m')]=String(now()-119000)");pg.wait_for_timeout(2500)
    print('nach Ablauf',hud(ev));assert 'Radar' not in hud(ev) and not ev("!!document.querySelector('.leaflet-overlay-pane svg.bmr')") and 'Hunter-Radar abgelaufen' in ev("__ts")
    # Satellitenbild
    ev("useRadar('d1a')");pg.wait_for_timeout(500);assert any(x.startswith('Satellitenbild: 2 Hunter erfasst') for x in ev("__ts")),ev("__ts")
    # Ende-Meldungen: Satellitenbild und Schutz
    ev("radar.t=now()-59000");pg.wait_for_timeout(2500);assert 'Satellitenbild abgelaufen' in ev("__ts"),ev("__ts")
    ev("__T.games.K7QF.players.u2.immUntil=now()+1500;notify()");pg.wait_for_timeout(3500)
    assert any(x.startswith('Schutz abgelaufen') for x in ev("__ts")),ev("__ts")
    # Meeting-Wahl: Knöpfe
    ev("__T.games.K7QF.tasks.m1={t0:Date.now()-1000,a:'u2',b:'u3',loc:{lat:47.072,lng:15.442}};notify()");pg.wait_for_timeout(800)
    pb=ev("$('pb').innerText");assert 'Wähle deinen Bonus' in pb,pb
    ev("[...$('pb').querySelectorAll('button.ggo')].find(b=>b.innerText==='Wählen').click()");pg.wait_for_timeout(300)
    btn=ev("[...$('gd').querySelectorAll('button')].map(b=>b.innerText.replace(/\\n/g,' ')).join('|')");print('Meeting',btn)
    assert 'Hunter-Radar' in btn and 'Satellitenbild' in btn and 'Immunität' not in btn
    ev("[...$('gd').querySelectorAll('button.gopt')][1].click()");pg.wait_for_timeout(200)
    ev("[...$('gd').querySelectorAll('button')].find(b=>/Wahl einloggen/.test(b.innerText)).click()");pg.wait_for_timeout(600)
    assert ev("__T.games.K7QF.tasks.m1.p.u2.c")=='rad' and 'Eingeloggt' in ev("$('gd').innerText")
    shot(pg,'meeting_wahl.png')
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
# ---------- Hunter
with app() as (pg,ev,errs):
    ev("window.__ts=[];const _t=toast;toast=(x,...r)=>{__ts.push(x);return _t(x,...r)}")
    setup(ev,'u1');pg.wait_for_timeout(1500)
    pb=ev("$('pb').innerText");print(pb.replace('\n',' | ')[:500]);assert 'Hider-Radar' in pb and 'Zeitbonus' in pb
    ev("bfClose()");ev("document.querySelector('button.gb').click()");pg.wait_for_timeout(300);print(ev("$('gd').innerText").replace('\n',' | '))
    ev("[...$('gd').querySelectorAll('button')].find(b=>b.innerText==='Übernehmen').click()");pg.wait_for_timeout(600)
    assert ev("__T.games.K7QF.hb.u1.time.k")=='bm'
    # Lena 50 m, Max 80 m (immun), Tom weit weg
    ev("pos={lat:47.0705,lng:15.4405}");mv(ev,'u3',80);ev("__T.games.K7QF.players.u3.immUntil=Date.now()+60000;notify()")
    ev("hbUse('time')");pg.wait_for_timeout(1500)
    print('HUD',hud(ev));assert 'Radar 1' in hud(ev)   # Lena (0 m) ja, Max immun nein
    ev("__T.games.K7QF.players.u3.immUntil=0;notify()");pg.wait_for_timeout(1300);assert 'Radar 2' in hud(ev)
    ev("__T.games.K7QF.players.u2.state='caught';notify()");pg.wait_for_timeout(1300);assert 'Radar 1' in hud(ev)
    print('Meldungen',ev("__ts.filter(x=>/Radar/.test(x))"))
    assert ev("__ts").count('Hider-Radar: 1 Hider in der Nähe')>=1
    shot(pg,'radar_hunter.png')
    ev("__T.games.K7QF.live={u3:{u1:now()+1500}};notify()");pg.wait_for_timeout(3500)
    assert 'Live-Standort von Max abgelaufen' in ev("__ts"),ev("__ts")
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
