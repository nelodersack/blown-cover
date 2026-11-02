# Test: Replay zeigt Hunter-/Hider-Radar als Sonar-Kreis, solange es läuft; Puls bei Gegnern im Umkreis
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{
      const T0=1800000000000,R0=T0+60000,s={r0:500,rMin:200,shrink:5,step:50,head:1,dur:30,ping:120,pen:2,mode:'survive',hbC:0,hbL:60,hbT:5,bon:true,mtN:1};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'},{id:'u3',name:'Max',role:'hider',col:2,j:3,state:'alive'}];
      const tr={u1:[],u2:[],u3:[]};for(let i=0;i<=60;i++){const t=R0+i*30000,d=i<20?400:i<26?60:400;tr.u1.push([t,47.0705+d/111320,15.4405,10]);tr.u2.push([t,47.0705,15.4405,10]);tr.u3.push([t,47.0705-300/111320,15.4405,10])}
      const m=R0+5*60000,log=[[m,'tasks/m1/t0',m],[m,'tasks/m1/a','u2'],[m,'tasks/m1/b','u3'],[m+60000,'tasks/m1/p/u2/c','bm'],[m+60000,'tasks/m1/p/u3/c','rad'],[m+61000,'tasks/m1/fin',m+61000],
        [R0+9*60000,'players/u2/used/m1m',true],[R0+5*60000,'hb/u1/time/k','bm'],[R0+5*60000,'hb/u1/time/av',R0+5*60000],[R0+20*60000,'hb/u1/time/u',R0+20*60000]];
      window.__f={format:'blown-cover-replay',v:2,code:'K7QF',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+30*60000,winner:'hider'},players:pl,tracks:tr,log};
      rvLoad(window.__f)})()""")
    pg.wait_for_timeout(500)
    print('radar',ev("JSON.stringify(RV.bms)"));assert ev("RV.bms.length")==2
    ov=lambda:ev("[...document.querySelectorAll('.leaflet-overlay-pane svg.bmr')].map(e=>e.classList.contains('hit'))")
    def at(mn):ev("RV.t=RV.f.game.R0+%d;rvDraw()"%(mn*60000));pg.wait_for_timeout(100);return ov()
    print('8 min',at(8));assert at(8)==[]
    print('9,5 min',at(9.5));assert at(9.5)==[False]                    # Hunter-Radar von Lena, Anna 400 m weg
    print('10,5 min',at(10.5));assert at(10.5)==[True]                  # Anna 60 m nah: Puls
    ev("map.setView([47.0705,15.4405],17,{animate:false})");at(10.5);shot(pg,'replay_radar.png')
    print('12 min',at(12));assert at(12)==[]                            # 2 Min (Ping-Intervall) vorbei
    print('20,5 min',at(20.5));assert at(20.5)==[False]                 # Hider-Radar von Anna: Lena 400 m weg
    assert any('Hider-Radar' in x for x in ev("RV.ev.map(e=>e.x)"))
    rvc=ev("rvClose();document.querySelectorAll('.leaflet-overlay-pane svg.bmr').length");assert rvc==0
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
