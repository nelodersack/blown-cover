# Test: lobby einstellungen
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:120,pen:1,mode:'survive',taskR:0,imm:120,shOn:true,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:40,hbT:15,gw:20,gd:60,ot:3},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T}},cols:{0:'u1',1:'u2',2:'u3'}}};
      uid='u1';pos={lat:47.069,lng:15.4385};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},500)")
    ev("tabGo('lt','set')");ev("ui.adv=true;ui.open.tasks=1;ui.open.zone=1;ui.open.game=1;ui.open.hb=1;panel(1)")
    ev("setHk(1);G.s.ddN=1;__T.games.K7QF.s.ddN=1;__T.games.K7QF.s.mtN=1;notify()");pg.wait_for_timeout(500)
    ev("document.getElementById('pb').scrollTop=0")
    pg.set_viewport_size({'width':420,'height':1900});pg.wait_for_timeout(300)
    pg.locator('#panel').screenshot(path=__import__('harness').OUT+'/lobby_einstellungen.png')
    print(ev("document.getElementById('pb').innerText.replace(/\\n/g,' | ').slice(0,1800)"))
    print('errors:',errs[:5])
