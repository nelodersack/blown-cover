# Test: „Fang starten“ (Fang ohne Verfolgungsjagd): Hunter löst aus, Hider bekommt Alarm nur in Reichweite, „Ich bleibe stehen“, Fang-Alarm darüber, Entkommen mit Schutz, Ping-Ausfall und Live-Hunter
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:550,rMin:250,shrink:2,step:50,head:3,dur:30,ping:150,pen:2,mode:'survive',taskR:0,imm:120,shOn:false,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:5,fs:true,fsR:40,fsT:40}"
PL="""u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0708,lng:15.4405,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0706,lng:15.4405,ts:T},
  u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0726,lng:15.4430,ts:T},u4:{name:'Tom',role:'hunter',state:'alive',j:4,col:3,lat:47.0680,lng:15.4380,ts:T}"""
def setup(ev,me):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',rn:0,startAt:T-9*60000,c:{lat:47.07,lng:15.44},s:%s,players:{%s},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}}};
      uid='%s';const p=__T.games.K7QF.players['%s'];pos={lat:p.lat,lng:p.lng};lastFix=Date.now()})()"""%(S,PL,me,me))
    ev("join('K7QF')")
    ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)")
    ev("window.__toasts=[];const _t=toast;window.toast=m=>{__toasts.push(String(m));return _t(m)}")
def pe(errs): assert not [e for e in errs if 'PE:' in e],errs

# 1 Hunter löst aus
with app(390,844) as (pg,ev,errs):
    setup(ev,'u1');pg.wait_for_timeout(1500);ev("typeof bfClose==='function'&&bfClose()");pg.wait_for_timeout(300)
    assert ev("!!document.querySelector('#pb button.fsb')"),'Knopf fehlt'
    pg.screenshot(path=OUT+'/fs_hunter_knoepfe.png')
    pg.click('#pb button.fsb');pg.wait_for_timeout(400)
    t=ev("document.getElementById('pb').textContent");assert 'Wen hast du im Visier?' in t and 'Lena' in t and 'Max' in t
    pg.click("#pb button.cgt:has-text('Lena')");pg.wait_for_timeout(700)
    f=ev("G.fz&&G.fz.u2");print('fz',f);assert f and f['h']=='u1'
    t=ev("document.getElementById('pb').textContent");assert 'Fang auf Lena gestartet' in t and 'Wieder in' in t,t[:400]
    pg.screenshot(path=OUT+'/fs_hunter_countdown.png')
    ev("fsBtn()");assert 'wieder in' in ev("__toasts.slice(-1)[0]")
    # zweite Auslösung auf denselben Hider während Countdown eines anderen Hunters wird nicht geschrieben
    ev("const m=fsMine();m.l-=70000;m.p={};LS[fsKey('fs')]=JSON.stringify(m)");ev("const t0=G.fz.u2.t;fsGo('u2');window.__t0=t0");pg.wait_for_timeout(400)
    assert ev("G.fz.u2.t===__t0"),'laufender Countdown wurde überschrieben'
    pe(errs)

# 2 Hider in Reichweite
with app(390,844) as (pg,ev,errs):
    setup(ev,'u2');pg.wait_for_timeout(1500);ev("typeof bfClose==='function'&&bfClose()")
    ev("__T.games.K7QF.fz={u2:{h:'u1',t:Date.now()-2000}};notify()");pg.wait_for_timeout(1500)
    assert ev("!!document.getElementById('fz')"),'kein Alarm';assert ev("FSH.ok===true")
    assert ev("__T.fzp&&__T.fzp.K7QF&&__T.fzp.K7QF.u2&&__T.fzp.K7QF.u2.ok===true")
    pg.screenshot(path=OUT+'/fs_hider_alarm.png')
    pg.click("#fz button.fy");pg.wait_for_timeout(1200)
    assert not ev("!!document.getElementById('fz')") and ev("!!document.querySelector('#pb .card.fzh')") and ev("!!document.querySelector('#pb .chip.fzc')")
    assert ev("FSH.a>0")
    pg.screenshot(path=OUT+'/fs_hider_karte.png')
    # Fang-Alarm liegt darüber
    ev("__T.games.K7QF.catches={u2:{hunter:'u4',t:Date.now()-2000,status:'pending'}};notify()");pg.wait_for_timeout(1200)
    assert ev("getComputedStyle(document.getElementById('fa')).zIndex")>'2300'
    ev("__T.games.K7QF.catches={};notify()");pg.wait_for_timeout(800)
    # Ablauf ohne Fang -> entkommen
    ev("FSH.t0-=40000;fsSave()");pg.wait_for_timeout(1600)
    me=ev("G.players.u2");print('imm',me.get('immUntil'),'pS',me.get('pS'))
    assert me.get('immUntil') and me.get('pS') and me['pS']>me['immUntil'] and any('Entkommen' in x for x in ev("__toasts"))
    assert ev("FSX&&FSX.h==='u1'")
    ev("draw()");pg.wait_for_timeout(400)
    assert ev("(()=>{let n=0;lay.eachLayer(l=>{if(l._mkk==='pu1'||(l.options&&l.options.icon&&/polygon/.test((l.options.icon.options||{}).html||'')))n++});return n})()")>=1
    pg.screenshot(path=OUT+'/fs_hider_entkommen.png')
    assert ev("fsSkip(G.players.u2,G.players.u2.pS+1000)") and not ev("fsSkip(G.players.u2,G.players.u2.pS+150000)")
    pe(errs)

# 3 Hider zu weit weg / ohne „Ich bleibe stehen“
with app(390,844) as (pg,ev,errs):
    setup(ev,'u3');pg.wait_for_timeout(1500);ev("typeof bfClose==='function'&&bfClose()")
    ev("__T.games.K7QF.fz={u3:{h:'u1',t:Date.now()-2000}};notify()");pg.wait_for_timeout(1500)
    assert not ev("!!document.getElementById('fz')") and ev("FSH.ok===false")
    pe(errs)
with app(390,844) as (pg,ev,errs):
    setup(ev,'u2');pg.wait_for_timeout(1500);ev("typeof bfClose==='function'&&bfClose()")
    ev("__T.games.K7QF.fz={u2:{h:'u1',t:Date.now()-2000}};notify()");pg.wait_for_timeout(1300)
    assert ev("!!document.getElementById('fz')")
    ev("FSH.t0-=40000;fsSave()");pg.wait_for_timeout(1600)
    assert not ev("!!document.getElementById('fz')") and not ev("G.players.u2.immUntil") and not ev("FSX")
    pe(errs)
print('errors: []')
