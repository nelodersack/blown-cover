# Test: Replay im Kopfgeld-Modus (KONZEPT_Kopfgeld_Replay.md)
# Erzeugte Runde: 3 Teams à 2 Hunter, 3 Hider. Agentur 1 (p1) kommt Mia auf 20 m nahe, die Füchse (p2) fangen sie kurz danach
# → Kopf-an-Kopf + Vor der Nase weggeschnappt; Agentur 3 (p3) fängt Ben später. Funk: Teamchats, Marker.
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot

REPLAY="""(()=>{const T0=1800000000000,R0=T0+120000,M=6e4,s={r0:700,rMin:300,shrink:5,step:50,head:2,dur:30,ping:120,pen:2,mode:'bounty',tN:3,imm:120,bon:true,hbC:60,hbL:60,hbOn:true,rp:true};
  const P_=(x,y)=>[+(47.07+y/111195).toFixed(6),+(15.44+x/75780).toFixed(6)],lin=(a,b,f)=>[a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f];
  // Weg als Liste [minute, x, y]; dazwischen linear
  const path=pts=>t=>{const m=(t-R0)/M;let i=0;while(i<pts.length-1&&pts[i+1][0]<=m)i++;const a=pts[i],b=pts[Math.min(i+1,pts.length-1)];const f=b[0]===a[0]?0:Math.max(0,Math.min(1,(m-a[0])/(b[0]-a[0])));return lin([a[1],a[2]],[b[1],b[2]],f)};
  const W={p1:path([[-2,-300,0],[8,80,0],[9,80,0],[12,-100,40],[30,-150,-200]]),p4:path([[-2,-250,50],[10,-50,150],[30,-200,300]]),
    p2:path([[-2,100,-420],[7,100,-80],[10,100,-2],[30,150,-100]]),p5:path([[-2,300,-300],[30,250,-50]]),
    p3:path([[-2,-200,520],[15,-200,205],[30,-100,300]]),p6:path([[-2,-400,400],[30,-350,100]]),
    p7:path([[-2,0,50],[5,100,0],[30,100,0]]),p8:path([[-2,-200,200],[30,-200,200]]),p9:path([[-2,0,-200],[15,40,-230],[30,0,-200]])};
  const tr={};Object.keys(W).forEach(k=>{tr[k]=[];for(let t=T0;t<=R0+30*M;t+=5000){const q=W[k](t),ll=P_(q[0],q[1]);tr[k].push([t,ll[0],ll[1],8])}});
  const H=(id,n,tm,col,j)=>({id,name:n,role:'hunter',col,tm,tmn:null,j,state:'alive'}),X=(id,n,col,j)=>({id,name:n,role:'hider',col,j,state:'alive'});
  const pl=[H('p1','Anna',1,0,1),H('p2','Bert',2,4,2),H('p3','Cora',3,6,3),H('p4','Dani',1,0,4),H('p5','Emil',2,4,5),H('p6','Finn',3,6,6),X('p7','Mia',1,7),X('p8','Ben',2,8),X('p9','Lea',3,9)];
  const c1=R0+10*M,c2=R0+15*M,xp=R0+11*M+20000;
  const log=[[c1,'catches/p7/hunter','p2'],[c1,'catches/p7/status','done'],[c1,'players/p7/state','caught'],[c1,'players/p7/sT',c1],
    [c2,'catches/p8/hunter','p3'],[c2,'catches/p8/status','done'],[c2,'players/p8/state','caught'],[c2,'players/p8/sT',c2],
    [xp,'hb/p4/b1/k','xp'],[xp,'hb/p4/b1/u',xp]];
  const ch=[[R0+6*M,'p1','t1','Mia läuft Richtung Osten, ich bin dran'],[R0+7*M,'p4','t1','Ich komme von Norden'],[R0+7*M+30000,'p2','t2','Mia steht am Teich'],
    [R0+8*M,'p7','hider','Achtung, zwei Teams bei mir!'],[R0+9*M+20000,'p1','t1','Verdammt, Füchse sind schneller'],[R0+12*M,'p3','t3','Ben bleibt am Spielplatz']];
  const e1=P_(100,0),pn=P_(-200,230);
  const mk=[[R0+8.5*M,'+','m1','excl',e1[0],e1[1],null,null,'p1','p7'],[R0+5*M,'+','m2','pin',pn[0],pn[1],null,'Spielplatz','p3',null],[R0+16*M,'-','m2'],[R0+9*M,'+','m3','zone',e1[0],e1[1],120,null,'p2',null]];
  rvLoad({format:'blown-cover-replay',v:2,code:'KPRP',round:0,game:{s,c:{lat:47.07,lng:15.44},teams:{1:{name:'Agentur 1',col:0},2:{name:'Die Füchse',col:4},3:{name:'Agentur 3',col:6}},startAt:T0,R0,end:R0+30*M,winner:'hunter'},
    players:pl,tracks:tr,log,funk:{ch,mk}});window.__R0=R0})()"""

with app(width=412,height=915) as (pg,ev,errs):
    ev("G=null;code=null;"+REPLAY);pg.wait_for_timeout(2500)
    st=ev("({fast:RV.st.fast,h2h:RV.st.h2h.map(e=>[e.a,e.b,e.hider,e.by,Math.round(e.d)]),sn:RV.st.snatch.map(e=>[e.a,e.b,e.hider,Math.round(e.d)]),wt:RV.wt,tc:RV.tc,vw:RV.vw})")
    print('Statistik:',st)
    assert st['fast'][0][0]==2 and st['wt']=='2' or st['wt']==2, st
    assert any(h[:3]==[1,2,'p7'] and h[3]==2 for h in st['h2h']), st['h2h']
    assert any(x[:3]==[1,2,'p7'] for x in st['sn']), st['sn']
    assert st['vw']==['all','t1','t2','t3','x']
    print('Kopfzeile:',ev("$('pb').querySelector('.rvop').innerText"))
    assert 'Sieg: Die Füchse' in ev("$('pb').querySelector('.rvop').innerText")
    # Alle, Minute 9:30
    ev("RV.t=__R0+9.5*6e4;rvDraw()");pg.wait_for_timeout(300)
    al=ev("Object.keys(RV.m).filter(k=>RV.m[k]).sort()");fm=ev("Object.keys(RV.fm).sort()")
    print('Alle: Marker',al,'Funkmarker',fm,'Funk:',ev("$('rvK').innerText").replace('\n',' | '))
    assert len(al)==9 and fm==['m1','m2','m3']
    shot(pg,'kopfgeld_replay_alle.png')
    # Sicht Agentur 1
    ev("rvView('t1');RV.t=__R0+9.5*6e4;rvDraw()");pg.wait_for_timeout(300)
    vm=ev("Object.fromEntries(Object.keys(RV.m).filter(k=>RV.m[k]).map(k=>[k,RV.m[k]._k]))");fm=ev("Object.keys(RV.fm).sort()")
    print('Agentur 1:',vm,fm,'Funk:',ev("$('rvK').innerText").replace('\n',' | '))
    assert set(vm)=={'p1','p4','p7','p8','p9'} and all(vm[k].startswith('ping') for k in ('p7','p8','p9')), vm
    assert fm==['m1'] and 'Füchse sind schneller' in ev("$('rvK').innerText") and 'Teich' not in ev("$('rvK').innerText")
    tl=ev("RV.ev.filter(rvVis).filter(e=>e.k==='bonus').length")
    shot(pg,'kopfgeld_replay_team.png')
    ev("$('panel').classList.remove('m');panel(1)");pg.wait_for_timeout(400);ev("$('ps').scrollTop=9999");pg.wait_for_timeout(200);shot(pg,'kopfgeld_replay_funk.png');ev("$('panel').classList.add('m');pMidSet()")
    # Extra-Ping von Agentur 1 → Doppelring
    ev("RV.t=__R0+11.5*6e4;rvDraw()");x=ev("RV.m.p9&&RV.m.p9._k");print('nach Extra-Ping:',x);assert x and x.startswith('xping')
    # Sicht Füchse: kein Extra-Ping (gehört Agentur 1)
    ev("rvView('t2');RV.t=__R0+11.5*6e4;rvDraw()");x=ev("RV.m.p9&&RV.m.p9._k");print('Füchse:',x);assert x and x.startswith('ping')
    assert ev("Object.keys(RV.fm).sort().join()")=='m3'
    # Sicht Hider: keine Hunter
    ev("rvView('x');RV.t=__R0+9.5*6e4;rvDraw()");vm=ev("Object.keys(RV.m).filter(k=>RV.m[k]).sort()");print('Hider:',vm)
    assert vm==['p7','p8','p9'] and 'zwei Teams' in ev("$('rvK').innerText")
    shot(pg,'kopfgeld_replay_hider.png')
    # Statistik
    ev("rvView('all');RV.tab='stat';RV.open={kk:1,ws:1};panel(1)");pg.wait_for_timeout(300)
    print('Statistik-Reiter:',ev("$('pb').innerText").replace('\n',' | ')[:400])
    shot(pg,'kopfgeld_replay_statistik.png')
    print('errors:',errs[:8])
    assert not errs

# 2) Aufnahme: Hunter u0 (Team 1) sieht Teammarker, schreibt im Teamchat; nach Rundenende landen Chat + Marker im Upload rp/<code>/<uid>,
#    Replay aus dem Endscreen zeigt Funk und Teamfarben (auch wenn G noch gesetzt ist)
import json
pl={}
for i,n in enumerate(['Anna','Bert','Cora','Dani','Gabi','Hugo']):
    p={'name':n,'role':'hunter' if i<4 else 'hider','state':'alive','j':i+1,'col':i+4}
    if i<4:p['tm']=i%2+1;p['tj']=100+i
    p.update({'lat':47.07+i*3e-4,'lng':15.44+i*3e-4,'ts':0});pl['u%d'%i]=p
with app(width=412,height=915) as (pg,ev,errs):
    ev("""(()=>{const T=Date.now();__T['.info']={connected:true};const pl=%s;for(const k in pl)pl[k].ts=T;
      __T.games={KPRA:{host:'u0',status:'running',startAt:T-10*6e4,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:2,head:0,rp:true}),players:pl,teams:{1:{name:'Die Füchse',col:2},2:{name:'Agentur 2',col:9}}}};
      notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=T})()"""%json.dumps(pl))
    ev("join('KPRA')");pg.wait_for_timeout(1200)
    ev("""(()=>{const T=now();__T.tmarks={KPRA:{1:{m1:{u:'u2',k:'pin',lat:47.071,lng:15.441,t:T,x:'Brücke'}}}};
      __T.chats={KPRA:{t1:{a:{u:'u0',n:'Anna',t:T-60000,x:'Ich nehme den Norden',r:'hunter'},b:{u:'u2',n:'Cora',t:T-30000,x:'Pin an der Brücke',r:'hunter'}},t2:{c:{u:'u1',n:'Bert',t:T,x:'Geheim',r:'hunter'}}}};notify()})()""")
    pg.wait_for_timeout(600)
    print('RP.mk:',ev("RP&&RP.mk"))
    assert ev("RP.mk.length")==1
    ev("__T.games.KPRA.status='over';__T.games.KPRA.winner='hunter';notify()");pg.wait_for_timeout(1500)
    up=ev("JSON.parse(((__T.rp||{}).KPRA||{}).u0||'{}')")
    print('Upload:',{k:up.get(k) for k in ('cn','ch','mk')})
    assert up.get('cn')=='t1' and len(up['ch'])==2 and 'Geheim' not in json.dumps(up) and len(up['mk'])==1
    ev("rpView()");pg.wait_for_timeout(1500)
    f=ev("({ch:RV.ch.length,mk:RV.mki.length,teams:RV.teams,col:colOf('p1'),pcol:PAL[RV.pl.p1.col%12],name:nm0('p1')})")
    print('Replay aus Endscreen:',f)
    assert f['ch']==2 and f['mk']==1 and f['col']==f['pcol']=='#00694a' and f['name']=='Anna'
    print('errors:',errs[:8])
    assert not errs
