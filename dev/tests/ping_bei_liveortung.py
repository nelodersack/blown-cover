# Test: ping bei liveortung
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',startAt:T-8000,c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:10,pen:2,mode:'survive',imm:120,shOn:false,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:0},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T,revealUntil:T+60000},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T},u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0707,lng:15.4407,ts:T,out:true}},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}}};
      uid='u1';pos={lat:47.069,lng:15.4385};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},500)")
    pg.wait_for_timeout(5000)
    print('ping pts:',ev("Object.keys(ping&&ping.pts||{}).join()"),'| out markers',ev("document.querySelectorAll('.mkw.out').length"))
    print('errors:',errs[:5])
