# Test: Durchsicht 14.11. – Meldungen stapeln, Voreinstellungen = Balancing für 2 Hunter/4 Hider, Regler ändert auch den Radius,
# Balancing-Zeile im Klartext, Kompass in der Lobby, Zombie-Grün und Zombie-Texte, neues Spiel mit Standardwerten
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:600,rMin:250,shrink:2,step:40,head:3,dur:30,ping:180,pen:1,mode:'%s',taskR:0,imm:180,shOn:true,shT:10,evT:5,ddN:1,ddT:4,mtN:1,mtT:8,bon:true,hbOn:true,hbN:2,hbC:90,hbL:50,hbT:15,gw:20,gd:60,ot:3}"
PL="""u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0709,lng:15.4402,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0706,lng:15.4405,ts:T},
  u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.4425,ts:T},u4:{name:'Tom',role:'hunter',state:'alive',j:4,col:3,lat:47.0688,lng:15.4385,ts:T},
  u5:{name:'Ben',role:'hider',state:'alive',j:5,col:4,lat:47.0682,lng:15.4378,ts:T},u6:{name:'Jana',role:'hider',state:'alive',j:6,col:5,lat:47.0695,lng:15.4412,ts:T}"""
def game(ev,pg,me,status='lobby',mode='survive',extra=''):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'%s',rn:0,%s c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5',5:'u6'}}};const g=__T.games.K7QF;%s
      uid='%s';const p=g.players['%s'];pos={lat:p.lat,lng:p.lng};lastFix=Date.now()})()"""%(status,"startAt:T-180000-400000," if status!='lobby' else '',S%mode,PL,extra,me,me))
    ev("join('K7QF')");pg.wait_for_timeout(1400);ev("typeof bfClose==='function'&&bfClose()")
    ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)");pg.wait_for_timeout(400)
def pe(errs): assert not [e for e in errs if 'PE:' in e],errs

# 1 Lobby: Voreinstellungen, Regler, Balancing-Zeile, Kompass
for W,H in [(390,844),(360,640)]:
  with app(W,H) as (pg,ev,errs):
    game(ev,pg,'u1')
    p30=ev("preOf(30)");p60=ev("preOf(60)");print(p30);print(p60)
    assert (p30['r0'],p30['rMin'],p30['head'],p30['ping'],p30['ddN'],p30['mtN'])==(600,250,3,180,1,1),p30
    assert (p60['r0'],p60['rMin'],p60['head'],p60['ping'])==(900,400,5,290),p60
    b=ev("balCalc({dur:30,mode:'survive'},2,4,2,1).o");assert all(p30[k]==v for k,v in b.items()),(b,p30)
    assert ev("balCalc({dur:30},2,4,0,1).o.r0")==700 and ev("balCalc({dur:30},2,4,4,1).o.r0")==500 and ev("balCalc({dur:30},2,4,4,1).o.ping")==120
    z=ev("balCalc({dur:30,mode:'zombie'},1,5,2,1).o");assert (z['r0'],z['rMin'],z['ping'])==(650,400,110),z   # Zombie unverändert
    # Kompass: an, aber vom Panel verdeckt -> unsichtbar; Panel eingeklappt -> sichtbar
    ev("rotOn=true;nbPaint()");pg.wait_for_timeout(200)
    assert ev("getComputedStyle(document.getElementById('nb')).visibility")=='hidden',ev("document.getElementById('nb').getBoundingClientRect().bottom+' '+document.getElementById('panel').getBoundingClientRect().top")
    ev("document.getElementById('panel').classList.remove('m');document.getElementById('panel').classList.add('c');nbFit()");pg.wait_for_timeout(400);ev("nbFit()")
    assert ev("getComputedStyle(document.getElementById('nb')).visibility")=='visible'
    ev("document.getElementById('panel').classList.remove('c');document.getElementById('panel').classList.add('m');pMidSet()")
    ev("tabGo('lt','set')");pg.wait_for_timeout(400)
    t=ev("document.getElementById('pb').textContent");assert '✓ Ausgeglichen' in t and 'anpassen' not in t.split('Balancing')[1][:40],t[:300]   # Werte = Balancing für 2/4
    ev("setPre(60)");pg.wait_for_timeout(400);assert ev("G.s.r0")==900 and ev("G.s.ping")==290 and ev("G.s.dur")==60
    ev("__T.games.K7QF.players.u7={name:'Kim',role:'hider',state:'alive',j:7,col:6,lat:47.07,lng:15.44,ts:Date.now()};notify()");pg.wait_for_timeout(500)
    t=ev("document.getElementById('pb').textContent");assert 'an 2 Hunter · 5 Hider anpassen' in t,t[:400]
    assert ev("document.documentElement.scrollWidth<=innerWidth") and ev("(()=>{const v=document.querySelector('#pb .balw').getBoundingClientRect();return v.right<=innerWidth-8})()")
    pg.screenshot(path=OUT+'/durchsicht_lobby_%d.png'%W);pe(errs)

# 2 Meldungen: zwei untereinander, gleiche nicht doppelt, dritte verdrängt die älteste
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u2','running')
    ev("document.getElementById('toast').innerHTML='';toast('Eins');toast('Zwei')");pg.wait_for_timeout(100)
    assert ev("[...document.querySelectorAll('#toast .t')].map(e=>e.textContent)")==['Eins','Zwei']
    ev("toast('Zwei')");assert ev("document.querySelectorAll('#toast .t').length")==2
    ev("toast('Drei')");assert ev("[...document.querySelectorAll('#toast .t')].map(e=>e.textContent)")==['Zwei','Drei']
    pg.screenshot(path=OUT+'/durchsicht_meldungen.png')
    pg.wait_for_timeout(3900);assert ev("document.querySelectorAll('#toast .t').length")==0
    pe(errs)

# 3 Zombie: Grün und Texte
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u1','running','zombie',"g.players.u2.role='hunter';g.players.u2.zt=T-200000;g.players.u2.zb='u1';g.players.u2.zd=T-150000;")
    pg.wait_for_timeout(1300)
    assert ev("document.body.classList.contains('zm')&&document.body.classList.contains('zmh')")
    t=ev("document.getElementById('pb').innerText+document.getElementById('hud').innerText");assert 'Hunter' not in t,t
    assert ev("zx('Die Hunter merken nichts. 2 Hunter, 1 Hunter, Hunter-Radar, den Huntern, ein Hunter läuft')")=='Die Zombies merken nichts. 2 Zombies, 1 Zombie, Zombie-Radar, den Zombies, ein Zombie läuft'
    assert ev("getComputedStyle(document.querySelector('.mkw.mate svg polygon')).stroke")=='rgb(126, 224, 74)'
    ev("map.setView([47.0706,15.4404],18,{animate:false})");pg.wait_for_timeout(400);pg.screenshot(path=OUT+'/durchsicht_zombie.png');pe(errs)
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u1','running');pg.wait_for_timeout(600)
    assert not ev("document.body.classList.contains('zm')") and ev("zx('Hunter-Radar')")=='Hunter-Radar';pe(errs)

# 4 Neues Spiel: Standardwerte = Balancing 2/4 für 60 Min
with app(390,844) as (pg,ev,errs):
    ev("__T['.info']={connected:true};notify();uid='u9';pos={lat:47.07,lng:15.44};lastFix=Date.now();window.appReady=()=>true")
    ev("document.getElementById('nm').value='Zoe';void mk()");pg.wait_for_timeout(2500)
    s=ev("G&&G.s");print(s);assert s and (s['r0'],s['rMin'],s['ping'],s['dur'],s['ddN'],s['mtN'],s['mode'])==(900,400,290,60,1,1,'survive'),s
    pe(errs)
print('errors: []')
