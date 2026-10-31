# Test: Meldung beim Zonenschrumpfen (Spiel + Replay), Replay-Zeitleiste, Hacking-Zone im Replay strichliert/voll
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    # Spiel: shrink 1 Min, nächster Schritt in ~3 s; danach rMin erreicht -> keine weitere Meldung
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',startAt:T-57000,c:{lat:47.07,lng:15.44},s:{r0:300,rMin:250,shrink:1,step:50,head:0,dur:30,ping:600,pen:1,mode:'survive',imm:120,shOn:false,hbOn:false,gw:20,gd:60,ot:0},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0701,lng:15.4401,ts:T}},cols:{0:'u1',1:'u2'}}};
      uid='u2';pos={lat:47.0701,lng:15.4401};lastFix=Date.now()})()""")
    ev("join('K7QF')")
    ev("window.__toasts=[];const _t=toast;toast=m=>{__toasts.push(m);_t(m)};setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},500)")
    pg.wait_for_timeout(6000)
    print('toasts:',ev("JSON.stringify(__toasts)"))
    ev("__T.games.K7QF.startAt-=60000;notify()");pg.wait_for_timeout(2500)
    print('toasts nach rMin:',ev("JSON.stringify(__toasts.filter(x=>/Zone/.test(x)))"))
    # Replay
    ev("""(()=>{G=null;code=null;
      const T0=1800000000000,R0=T0+60000,s={r0:500,rMin:300,shrink:5,step:50,head:1,dur:30,ping:120,pen:2,mode:'survive',hbC:60,hbL:60,hkZ:75,hkT:180,hkR:60,hkS:9,hkN:3,ozR:75,hk:true};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'}];
      const tr={u1:[],u2:[]};for(let i=0;i<=62;i++){const t=T0+i*30000;tr.u1.push([t,47.069,15.4385,10]);tr.u2.push([t,47.0705,15.4405,10])}
      const h0=R0+9*60000,log=[[h0,'tasks/hk/t0',h0],[h0,'tasks/hk/loc/lat',47.0705],[h0,'tasks/hk/loc/lng',15.4405],
        [h0+5000,'tasks/hk/at/1/s',h0+5000],[h0+5000,'tasks/hk/at/1/u','u2'],[h0+5000,'tasks/hk/at/1/p/u2/t',h0+5000],
        [h0+40000,'tasks/hk/at/1/e/k','ab'],[h0+40000,'tasks/hk/at/1/e/t',h0+40000]];
      rvLoad({format:'blown-cover-replay',v:2,code:'K7QF',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+30*60000,winner:'hider'},players:pl,tracks:tr,log})})()""")
    pg.wait_for_timeout(600)
    print('zone-ev:',ev("JSON.stringify(RV.ev.filter(e=>e.k==='zone').map(e=>rvTm(e.t,RV.f.game.R0)+' '+e.x))"))
    print('zs-striche:',ev("document.querySelectorAll('#rvT .zs').length"),'ping-striche:',ev("document.querySelectorAll('#rvT .pg').length"))
    for dt,l in ((9*60000+2000,'vor hack'),(9*60000+20000,'hack läuft'),(9*60000+60000,'abgebrochen')):
        ev("RV.t=RV.f.game.R0+%d;rvDraw()"%dt)
        print(l,'dash:',ev("RV.tkc.hk&&RV.tkc.hk.options.dashArray"),'weight:',ev("RV.tkc.hk&&RV.tkc.hk.options.weight"))
    ev("RV.t=RV.f.game.R0+5*60000-3000;RV.speed=10;rvPlay()");pg.wait_for_timeout(800)
    print('toast replay:',ev("__toasts.slice(-1)[0]"))
    pg.locator('#panel').screenshot(path=__import__('harness').OUT+'/zone_schrumpfen_timeline.png')
    print('errors:',errs[:8])
