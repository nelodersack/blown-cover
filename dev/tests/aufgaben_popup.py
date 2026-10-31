# Test: Popups der Aufgaben-Marker (Name + Belohnung) im Spiel und im Replay
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',startAt:T-60000,c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:600,pen:2,mode:'survive',taskR:0,imm:120,shOn:true,shT:0,evT:5,ddN:1,ddT:0,mtN:0,mtT:5,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:0,hk:true,hkZ:75,hkT:180,hkR:30,hkS:1,hkN:3,ozR:75},
      tasks:{hk:{t0:T-1000,loc:{lat:47.0705,lng:15.4405},rr:0},sh:{t0:T-5000,loc:{lat:47.0712,lng:15.4390},rr:0},d1:{t0:T-5000,loc:{lat:47.0690,lng:15.4410},a:'u2',b:'u3',rr:0}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0700,lng:15.4400,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0702,lng:15.4402,ts:T}},cols:{0:'u1',1:'u2',2:'u3'}}};
      uid='u2';pos={lat:47.0700,lng:15.4400};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(1500)
    print('ids:',ev("Object.keys(G.tasks).join()+' isDd(d1)='+isDd('d1')"))
    for cls in ('t-hk','t-sh','t-dd'):
        n=ev("document.querySelectorAll('.mkw.%s').length"%cls)
        if n:
            ev("(()=>{let m;lay.eachLayer(l=>{if(l.options&&l.options.icon&&String(l.options.icon.options.className).split(' ').includes('%s'))m=l});m.openPopup()})()"%cls);pg.wait_for_timeout(300)
            print(cls,'->',ev("(document.querySelector('.leaflet-popup-content')||{}).innerText||'KEIN POPUP'").replace('\n',' | '))
            if cls=='t-hk':shot(pg,'aufgaben_popup_hk.png')
            ev("map.closePopup()")
        else: print(cls,'kein Marker')
    # Replay
    ev("""(()=>{G=null;code=null;
      const T0=1800000000000,R0=T0+60000,s={r0:500,rMin:300,shrink:5,step:50,head:1,dur:30,ping:120,pen:2,mode:'survive',imm:120,bon:true,hbC:60,hbL:60,hkZ:75,hkT:180,hkR:60,hkS:9,hkN:3,ozR:75,hk:true};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'}];
      const tr={u1:[],u2:[]};for(let i=0;i<=62;i++){const t=T0+i*30000;tr.u1.push([t,47.069,15.4385,10]);tr.u2.push([t,47.0705,15.4405,10])}
      const h0=R0+9*60000,log=[[h0,'tasks/hk/t0',h0],[h0,'tasks/hk/loc/lat',47.0705],[h0,'tasks/hk/loc/lng',15.4405],[R0,'tasks/sh/t0',R0],[R0,'tasks/sh/loc/lat',47.0712],[R0,'tasks/sh/loc/lng',15.4390]];
      rvLoad({format:'blown-cover-replay',v:2,code:'K7QF',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+30*60000,winner:'hider'},players:pl,tracks:tr,log});RV.t=R0+10*60000;rvDraw()})()""")
    pg.wait_for_timeout(600)
    for cls in ('t-hk','t-sh'):
        if True:
            ev("RV.tk['%s'].eachLayer(l=>{if(l.getPopup())l.openPopup()})"%('hk' if cls=='t-hk' else 'sh'));pg.wait_for_timeout(300)
            print('  ->',ev("(document.querySelector('.leaflet-popup-content')||{}).innerText||'KEIN POPUP'").replace('\n',' | '))
            ev("map.closePopup()")
    print('errors:',errs[:8])
