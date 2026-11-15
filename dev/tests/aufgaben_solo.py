# Test: Schalter „Aufgabe geht allein weiter“ (s.tsol): Partner gefangen -> allein am markierten Ort, Ort für Hunter sichtbar, Belohnung bleibt;
# Partner ohne Fang weg -> allein, Ort geheim; Schalter aus -> wie bisher verfallen (Untertauchen)
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:600,rMin:250,shrink:2,step:40,head:3,dur:30,ping:180,pen:1,mode:'survive',taskR:0,imm:180,shOn:false,shT:10,evT:5,ddN:1,ddT:4,mtN:1,mtT:8,bon:true,hbOn:true,hbN:2,hbC:90,hbL:50,hbT:15,gw:20,gd:60,ot:3%s}"
PL="""u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0709,lng:15.4402,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0706,lng:15.4405,ts:T},
  u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.4425,ts:T},u4:{name:'Tom',role:'hunter',state:'alive',j:4,col:3,lat:47.0688,lng:15.4385,ts:T},
  u5:{name:'Ben',role:'hider',state:'alive',j:5,col:4,lat:47.0682,lng:15.4378,ts:T},u6:{name:'Jana',role:'hider',state:'alive',j:6,col:5,lat:47.0695,lng:15.4412,ts:T}"""
TK="tasks:{d1:{t0:T-60000,loc:{lat:47.0716,lng:15.4425},rr:0,a:'u2',b:'u3'},m1:{t0:T-60000,loc:{lat:47.0700,lng:15.4410},rr:0,a:'u5',b:'u6'}},"
def game(ev,pg,me,sol=True):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',rn:0,startAt:T-580000,%s c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5',5:'u6'}}};const g=__T.games.K7QF;
      uid='%s';const p=g.players['%s'];pos={lat:p.lat,lng:p.lng};lastFix=Date.now()})()"""%(TK,S%(',tsol:true' if sol else ''),PL,me,me))
    ev("join('K7QF')");pg.wait_for_timeout(1400);ev("typeof bfClose==='function'&&bfClose()")
    ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)");pg.wait_for_timeout(1500)
T_="__T.games.K7QF.tasks"
# 1 Hider: Partner gefangen -> allein + verraten, Belohnung nach Erledigen
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u3');ev("window.__m=[];const t0=toast;toast=function(x){__m.push(String(x));return t0.apply(this,arguments)}")
    ev("__T.games.K7QF.players.u2.state='caught';notify()");pg.wait_for_timeout(2600)
    d=ev(T_+".d1");assert d.get('sol')=='u3' and d.get('cmp') is True and not d.get('ex'),d
    ms=ev("__m");print(ms);assert any('allein' in x for x in ms) and any('Dead Drop kompromittiert' in x for x in ms),ms
    t=ev("document.getElementById('pb').textContent");assert 'Kompromittiert' in t and 'ohne Belohnung' not in t,t[:400]
    assert ev("document.querySelectorAll('.grow.cmp').length")==1 and ev("document.querySelectorAll('.tsq.cmp').length")>=1
    pg.screenshot(path=OUT+'/solo_hider.png')
    ev("chk('d1')");pg.wait_for_timeout(900);assert ev(T_+".d1.fin"),ev(T_+".d1")
    it=ev("myItems(G)");print(it);assert len(it)==1 and it[0]['id']=='d1b' and it[0]['type'] in('bm','radar'),it
    assert any('Deine Belohnung' in x for x in ev("__m"))
    assert not [e for e in errs if 'PE:' in e],errs
# 2 Hunter: sieht den verratenen Ort (Meeting), Meldung
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u1');ev("window.__m=[];const t0=toast;toast=function(x){__m.push(String(x));return t0.apply(this,arguments)}")
    assert ev("cmpIds(G,now()).length")==0
    ev("__T.games.K7QF.players.u5.state='caught';notify()");pg.wait_for_timeout(4200)
    m=ev(T_+".m1");assert m.get('sol')=='u6' and m.get('cmp') is True,m
    assert ev("cmpIds(G,now())")==['m1'];ms=ev("__m");print(ms);assert any('Meeting kompromittiert' in x for x in ms),ms
    assert ev("document.querySelectorAll('.leaflet-marker-icon').length")>0
    assert ev("document.querySelectorAll('.tsq.cmp').length")>=1
    pg.screenshot(path=OUT+'/solo_hunter.png')
    # erledigt -> Ort verschwindet
    ev(T_+".m1.fin=Date.now();notify()");pg.wait_for_timeout(1500);assert ev("cmpIds(G,now()).length")==0
    assert not [e for e in errs if 'PE:' in e],errs
# 2b Freier Hider ohne Aufgabe übernimmt zuerst, Ort bleibt geheim
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u3');ev("__T.games.K7QF.players.u7={name:'Kim',role:'hider',state:'alive',j:7,col:6,lat:47.071,lng:15.441,ts:Date.now()};notify()");pg.wait_for_timeout(600)
    ev("__T.games.K7QF.players.u2.state='caught';notify()");pg.wait_for_timeout(2600)
    d=ev(T_+".d1");assert d.get('a')=='u7' and not d.get('sol') and not d.get('cmp'),d
    # danach fällt auch Kim (gefangen), keiner mehr frei -> allein + verraten
    ev("__T.games.K7QF.players.u7.state='caught';notify()");pg.wait_for_timeout(2600)
    d=ev(T_+".d1");assert d.get('sol')=='u3' and d.get('cmp') is True,d
    assert not [e for e in errs if 'PE:' in e],errs
# 2c Dossier abgelegt, Ableger gefangen -> Ort verraten (Abholer bleibt)
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u1');ev(T_+".d1.dep={u:'u2',t:Date.now()};notify()");pg.wait_for_timeout(600)
    ev("__T.games.K7QF.players.u2.state='caught';notify()");pg.wait_for_timeout(3000)
    d=ev(T_+".d1");assert d.get('cmp') is True and d.get('b')=='u3' and not d.get('sol') and not d.get('fin'),d
    assert ev("cmpIds(G,now())")==['d1']
    assert not [e for e in errs if 'PE:' in e],errs
# 3 Partner ohne Fang weg (DQ): allein, Ort bleibt geheim
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u3');ev("__T.games.K7QF.players.u2.state='dq';notify()");pg.wait_for_timeout(2600)
    d=ev(T_+".d1");assert d.get('sol')=='u3' and not d.get('cmp'),d
    t=ev("document.getElementById('pb').textContent");assert 'Partner fällt aus' in t and 'Kompromittiert' not in t,t[:400]
# 4 Schalter aus (Untertauchen): verfällt wie bisher
with app(390,844) as (pg,ev,errs):
    game(ev,pg,'u3',sol=False);ev("__T.games.K7QF.players.u2.state='caught';notify()");pg.wait_for_timeout(2600)
    d=ev(T_+".d1");assert d.get('ex') is True and not d.get('sol') and not d.get('cmp'),d
# 5 Lobby: Schalter im Bereich Aufgaben
with app(390,844) as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();__T.games={K7QF:{host:'u1',status:'lobby',rn:0,c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1'}}};uid='u1';pos={lat:47.07,lng:15.44};lastFix=Date.now()})()"""%(S%'',PL))
    ev("join('K7QF')");pg.wait_for_timeout(1400);ev("setB('tsol','1')");pg.wait_for_timeout(400);assert ev("G.s.tsol")is True
    assert not [e for e in errs if 'PE:' in e],errs
    print('errors:',[e for e in errs])
