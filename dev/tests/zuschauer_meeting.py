# Test: Zuschauer sehen Meetings nicht als Kartenmarker (kein fester Ort), außer jemand muss es allein am Ort erledigen
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',startAt:T-600000,c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:180,pen:2,mode:'survive',imm:120,shOn:true,shT:0,ddN:1,ddT:0,mtN:1,mtT:0,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:0,gw:20,gd:60,ot:0},
      tasks:{m1:{t0:T-60000,a:'u2',b:'u3',loc:{lat:47.071,lng:15.441}},d1:{t0:T-60000,a:'u2',b:'u3',loc:{lat:47.069,lng:15.439}},sh:{t0:T-60000,loc:{lat:47.0695,lng:15.4395}}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T},
        u4:{name:'Tom',role:'hider',state:'caught',sT:T-100000,j:4,col:3,lat:47.068,lng:15.438,ts:T}},cols:{0:'u1',1:'u2',2:'u3',3:'u4'}}};
      uid='u4';pos={lat:47.068,lng:15.438};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(1200);ev("draw()")
    k=ev("[...document.querySelectorAll('.mkw')].map(e=>[...e.classList].find(c=>/^t-/.test(c))).filter(Boolean)");print('Zuschauer sieht',k)
    assert 't-mt' not in k and 't-dd' in k and 't-sh' in k
    ev("__T.games.K7QF.tasks.m1.sol='u2';notify()");pg.wait_for_timeout(500);ev("draw()")
    k=ev("[...document.querySelectorAll('.mkw')].map(e=>[...e.classList].find(c=>/^t-/.test(c))).filter(Boolean)");print('mit sol',k);assert 't-mt' in k
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
