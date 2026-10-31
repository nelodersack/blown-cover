# Test: replay hacking
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{
      const T0=1800000000000,R0=T0+60000,s={r0:500,rMin:200,shrink:5,step:50,head:1,dur:30,ping:120,pen:2,mode:'survive',hbC:60,hbL:60,hkZ:75,hkT:180,hkR:60,hkS:9,hkN:3,ozR:75,hk:true};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'},{id:'u3',name:'Max',role:'hider',col:2,j:3,state:'alive'}];
      const tr={u1:[],u2:[],u3:[]};for(let i=0;i<=40;i++){const t=R0+i*30000;tr.u1.push([t,47.069,15.4385,10]);tr.u2.push([t,47.0705,15.4405,10]);tr.u3.push([t,47.0710,15.4410,10])}
      const h0=R0+9*60000,log=[[h0,'tasks/hk/t0',h0],[h0,'tasks/hk/loc/lat',47.0705],[h0,'tasks/hk/loc/lng',15.4405],
        [h0+5000,'tasks/hk/at/1/s',h0+5000],[h0+5000,'tasks/hk/at/1/u','u2'],[h0+5000,'tasks/hk/at/1/p/u2/t',h0+5000],[h0+20000,'tasks/hk/at/1/p/u3/t',h0+20000],
        [h0+100000,'tasks/hk/at/1/e/k','ok'],[h0+100000,'tasks/hk/at/1/e/t',h0+100000],[h0+100000,'tasks/hk/res/k','ok'],[h0+100000,'tasks/hk/res/t',h0+100000],[h0+100000,'tasks/hk/res/a','1'],[h0+100000,'tasks/hk/res/el/u2',1],[h0+100000,'tasks/hk/res/el/u3',2],
        [h0+150000,'tasks/hk/cm/u','u2'],[h0+150000,'tasks/hk/cm/t',h0+150000],
        [h0+160000,'tasks/hk/oz/u','u1'],[h0+160000,'tasks/hk/oz/t',h0+160000],[h0+160000,'tasks/hk/oz/lat',47.0710],[h0+160000,'tasks/hk/oz/lng',15.4410]];
      window.__f={format:'blown-cover-replay',v:2,code:'K7QF',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+30*60000,winner:'hider'},players:pl,tracks:tr,log};
      rvLoad(window.__f)})()""")
    pg.wait_for_timeout(500)
    print('events:',ev("JSON.stringify(RV.ev.filter(e=>e.k!=='ping').map(e=>rvTm(e.t,RV.f.game.R0)+' '+e.k+' '+e.x))"))
    for dt,l in ((9*60000+30000,'hack'),(9*60000+120000,'after'),(9*60000+185000,'oz warn'),(9*60000+200000,'oz on')):
        ev("RV.t=RV.f.game.R0+%d;rvDraw()"%dt)
        print(l,'taskLayers',ev("Object.keys(RV.tk).filter(k=>RV.tk[k])"),'oz',ev("RV.ozK"),'live',ev("document.querySelectorAll('.mkw.live').length"))
    shot(pg,'replay_hacking_ende.png')
    print('errors:',errs[:8])
