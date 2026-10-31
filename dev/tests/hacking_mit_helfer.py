# Test: hacking mit helfer
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      const base={lat:47.07,lng:15.44};
      __T.games={K7QF:{host:'u1',status:'running',startAt:T-60000,c:base,s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:600,pen:2,mode:'survive',taskR:0,imm:120,shOn:false,shT:10,evT:5,ddN:0,ddT:5,mtN:0,mtT:5,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:0,hk:true,hkZ:75,hkT:20,hkR:30,hkS:1,hkN:3,ozR:75},
      tasks:{hk:{t0:T-1000,loc:{lat:47.0705,lng:15.4405},rr:0}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T},u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0600,lng:15.4300,ts:T}},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}}};
      uid='u2';pos={lat:47.0705,lng:15.4405};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now();pos={lat:47.0705,lng:15.4405}},500)")
    pg.wait_for_timeout(1500)
    print('card:',ev("document.getElementById('pb').innerText.replace(/\\n/g,' | ').slice(0,500)"))
    ev("hkJoin()");pg.wait_for_timeout(2500)
    print('at1:',ev("JSON.stringify(__T.games.K7QF.tasks.hk.at)"))
    print('hud:',ev("document.getElementById('hud').innerText.replace(/\\n/g,' ')"))
    print('act:',ev("hkAct(G,'u2')"),'loc?',ev("locatable(G.players.u2,Date.now(),'u2')"))
    ev("__T.games.K7QF.tasks.hk.at[1].p.u3={t:Date.now()}")
    pg.wait_for_timeout(9000)
    print('prog:',ev("hkProg(G,hkSt(G,now()).run||hkSt(G,now()).la,now())"),'pg',ev("JSON.stringify(__T.games.K7QF.tasks.hk.at[1].pg)"))
    pg.wait_for_timeout(10000)
    print('res:',ev("JSON.stringify(__T.games.K7QF.tasks.hk.res)"),'imm:',ev("__T.games.K7QF.players.u2.immUntil-Date.now()"))
    print('card2:',ev("document.getElementById('pb').innerText.replace(/\\n/g,' | ').slice(0,600)"))
    ev("hkCmUse()");pg.wait_for_timeout(1500)
    print('cm:',ev("JSON.stringify(__T.games.K7QF.tasks.hk.cm)"),'hud:',ev("document.getElementById('hud').innerText.replace(/\\n/g,' ')"))
    print('ev:',ev("JSON.stringify(Object.values(__T.games.K7QF.ev||{}).map(e=>e.x))"))
    print('errors:',errs[:8])
    shot(pg,'hacking_mit_helfer_ende.png')
