# Test: UX-Feinschliff (Lobby-Spalten, Einstellungsliste, HUD, Fang-Alarm, Fang-Raster, Chat-Schnellnachrichten, Zuschauer, Endscreen + Replay)
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:500,rMin:200,shrink:5,step:50,head:2,dur:60,ping:180,pen:2,mode:'survive',taskR:0,imm:240,shOn:true,shT:10,evT:5,ddN:1,ddT:4,mtN:1,mtT:8,bon:true,hbOn:true,hbN:2,hbC:90,hbL:60,hbT:30,gw:20,gd:60,ot:5,hk:true,hkZ:75,hkT:270,hkR:90,hkS:17,hkN:3,ozR:115,rp:true}"
def game(ev,me,status='running',el=140):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'%s',rn:0,startAt:T-120000-%d*1000,c:{lat:47.07,lng:15.44},s:%s,
      tasks:{d1:{t0:T-60000,a:'u2',b:'u4',loc:{lat:47.0712,lng:15.4415}},m1:{t0:T-60000,a:'u2',b:'u3',loc:{lat:47.072,lng:15.442}},
        sh:{t0:T-60000,loc:{lat:47.0690,lng:15.4390}},hk:{t0:T-60000,loc:{lat:47.0695,lng:15.4425},rr:0}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0725,lng:15.4385,ts:T},u5:{name:'Ben',role:'hunter',state:'alive',j:5,col:4,lat:47.0675,lng:15.4370,ts:T},
        u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.4430,ts:T},
        u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0680,lng:15.4380,ts:T},u6:{name:'Jana',role:'hider',state:'caught',sT:T-100000,j:6,col:5,lat:47.0685,lng:15.4390,ts:T}},
      catches:{u6:{hunter:'u1',t:T-100000,status:'done'}},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5',5:'u6'}}};
      uid='%s';pos={lat:__T.games.K7QF.players['%s'].lat,lng:__T.games.K7QF.players['%s'].lng};lastFix=Date.now()})()"""%(status,el,S,me,me,me))
def go(ev,pg):
    ev("join('K7QF')");pg.wait_for_timeout(1300);ev("typeof bfClose==='function'&&bfClose()")
    ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)")
def shot(pg,n):pg.screenshot(path=OUT+'/ux_'+n+'.png')

# 1 Lobby: Spalten, Wechseln, Einstellungsliste
with app(390,844) as (pg,ev,errs):
    game(ev,'u1','lobby');go(ev,pg);ev("$('panel').classList.remove('m','c')");pg.wait_for_timeout(400)
    r=ev("[...document.querySelectorAll('.lcol')].map(c=>c.querySelectorAll('.lchip').length)");print('Spalten',r);assert r==[2,4]
    assert ev("!!document.querySelector('.lchip.me')") and ev("document.querySelector('.lsw').textContent").startswith('+ Zu den Hidern')
    shot(pg,'lobby')
    ev("document.querySelector('.lsw').click()");pg.wait_for_timeout(400);assert ev("__T.games.K7QF.players.u1.role")=='hider'
    ev("tabGo('lt','set')");pg.wait_for_timeout(300)
    n=ev("document.querySelectorAll('.grp .acc.li').length");print('Listenzeilen',n);assert n>=7
    d=ev("(()=>{const b=document.querySelector('.grp .acc.li>button'),c=b.querySelector('.chv');return b.getBoundingClientRect().right-c.getBoundingClientRect().right})()");print('Pfeil-Abstand rechts',d);assert d<30
    ev("$('ps').scrollTop=400");shot(pg,'einstellungen')
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]

# 2 Hider: HUD, Chat, Fang-Alarm
with app(390,844) as (pg,ev,errs):
    game(ev,'u2');go(ev,pg);pg.wait_for_timeout(1200)
    l=ev("[...document.querySelectorAll('#hud .hp small')].map(e=>e.textContent)");print('HUD',l);assert l[0]=='Restzeit' and l[1].startswith('Zone') and l[2]=='Ping in'
    assert ev("!!document.querySelector('#hud .hp.hot')"),'Ping-Warnung fehlt (40 s von 180 s)'
    shot(pg,'hud')
    ev("chToggle(true)");pg.wait_for_timeout(400)
    q=ev("[...document.querySelectorAll('#chq button')].map(b=>b.textContent)");print('Schnell',q)
    assert 'Bin auf dem Weg zum Dead Drop' in q and 'Komme zum Meeting mit Max' in q and 'Gehe zum Terminal' in q
    assert 'Hidern' not in ev("document.querySelector('#chm .chc.on').dataset.e") and 'Hunter' in ev("document.querySelector('#chm .chc.on').dataset.e")
    shot(pg,'chat_leer')
    ev("(()=>{const r0=db.ref.bind(db);window.__P=[];db.ref=p=>{const r=r0(p);r.push=v=>{__P.push([p,v]);return Promise.resolve()};return r}})()")
    ev("[...document.querySelectorAll('#chq button')].find(b=>b.textContent==='Bin auf dem Weg zum Dead Drop').click()");pg.wait_for_timeout(400)
    m=ev("JSON.stringify(__P)");print(m[:160]);assert 'chats/K7QF/hider' in m and 'Bin auf dem Weg zum Dead Drop' in m
    ev("__T.games.K7QF.tasks.d1.dep={u:'u2',t:Date.now()};notify()");pg.wait_for_timeout(1300)
    q=ev("[...document.querySelectorAll('#chq button')].map(b=>b.textContent)");print('nach Ablage',q);assert 'Dead Drop liegt bereit' in q and 'Bin auf dem Weg zum Dead Drop' not in q
    shot(pg,'chat')
    ev("chShow('dm:u3')");pg.wait_for_timeout(300);q=ev("[...document.querySelectorAll('#chq button')].map(b=>b.textContent)");assert 'Komme zu dir' in q
    ev("chToggle(false)")
    ev("__T.games.K7QF.catches.u2={hunter:'u1',t:Date.now(),status:'pending'};notify()");pg.wait_for_timeout(1300)
    assert ev("$('fa').classList.contains('on')");n=int(ev("document.querySelector('#fa .fr>div').textContent"));print('Countdown',n);assert 25<=n<=30
    shot(pg,'fang_alarm')
    ev("[...document.querySelectorAll('#fa button')].find(b=>b.textContent==='Nein').click()");pg.wait_for_timeout(600)
    assert ev("__T.games.K7QF.catches.u2.status")=='denied' and not ev("$('fa').classList.contains('on')")
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]

# 3 Hunter: kein orangener Ping, Fang-Raster
with app(390,844) as (pg,ev,errs):
    game(ev,'u1');go(ev,pg);pg.wait_for_timeout(1200)
    assert not ev("!!document.querySelector('#hud .hp.hot')")
    ev("cc()");pg.wait_for_timeout(300);n=ev("document.querySelectorAll('.cgt').length");print('Fang-Raster',n);assert n==3
    shot(pg,'fang_melden')
    ev("chToggle(true)");pg.wait_for_timeout(400);q=ev("[...document.querySelectorAll('#chq button')].map(b=>b.textContent)");print('Hunter',q);assert 'Hider gesichtet!' in q
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]

# 4 Zuschauer
with app(390,844) as (pg,ev,errs):
    game(ev,'u6');go(ev,pg);ev("$('panel').classList.remove('m','c')");pg.wait_for_timeout(500)
    n=ev("document.querySelectorAll('button.zr').length");print('Zeilen',n);assert n==6
    assert ev("document.querySelectorAll('.zs').length")>=4
    ev("document.querySelector('button.zr').click()");pg.wait_for_timeout(300);assert ev("!!document.querySelector('.zd')")
    ev("chToggle(true)");pg.wait_for_timeout(300);assert ev("$('chq').style.display")=='none'
    ev("chToggle(false)");shot(pg,'zuschauer')
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]

# 5 Endscreen + Replay direkt
with app(390,844) as (pg,ev,errs):
    game(ev,'u2');go(ev,pg);pg.wait_for_timeout(800)
    ev("__T.games.K7QF.status='over';__T.games.K7QF.winner='hider';notify()");pg.wait_for_timeout(1800)
    t=ev("[...document.querySelectorAll('#resb .rhl small')].map(e=>e.textContent)");print('Kacheln',t);assert t[:2]==['Hider frei','Fänge']
    assert ev("$('res').style.display")=='flex' and ev("!!document.querySelector('#resb .rpb')")
    shot(pg,'ende')
    ev("document.querySelector('#resb .rpb').click()");pg.wait_for_timeout(1200)
    assert ev("!!RV") and ev("$('res').style.display")=='none';print('Replay offen, Spuren',ev("RV.tr"));assert ev("RV.tr")=='short'
    assert ev("!!document.querySelector('#pb .rvtab')") and ev("document.querySelector('#pb .rvtab').getBoundingClientRect().top<document.querySelector('#rvT').getBoundingClientRect().top")
    pg.wait_for_timeout(1500);assert ev("!!RV")  # Tick darf das Replay nicht stören
    shot(pg,'replay')
    ev("rvTr('all')");pg.wait_for_timeout(300);assert 'ganz' in ev("document.querySelector('.rvtr').textContent")
    ev("rvClose()");pg.wait_for_timeout(600);assert ev("$('res').style.display")=='flex'
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
