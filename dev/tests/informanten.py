# Test: Informanten im Kopfgeld (KONZEPT_Informanten.md)
# 1) Planung: Zeiten 20–80 %, Mindestabstand; Balancing 2 Teams → 1, 4 Teams → 2
# 2) Erscheinen: Ort in der Zone, ≥ 50 m zu Aufgaben; Hunter sieht Marker, Hider bekommt keinen Listener
# 3) Treffen in 30 m → Wahl → Abhören zeigt andere Teams; Störsender verzögert den Ping des Ziel-Teams um ½ Intervall
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
NM=['Anna','Bert','Cora','Dani','Emil','Finn','Gabi','Hugo','Ida','Jan']
def players():
    pl={}
    for i,n in enumerate(NM):
        u='u%d'%i;p={'name':n,'role':'hunter' if i<6 else 'hider','state':'alive','j':i+1,'col':i%12,'lat':47.07+i*3e-4,'lng':15.44+i*3e-4,'ts':0}
        if i<6:p['tm']=i%3+1;p['tj']=100+i
        pl[u]=p
    return pl
SET="""(()=>{const T=Date.now();__T['.info']={connected:true};const pl=%s;for(const k in pl)pl[k].ts=T;
  __T.games={INFO:{host:'u0',status:'running',startAt:T-600000,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:3,head:0,dur:30,ping:60,inf:true,infN:2,r0:600,rMin:300}),players:pl}};
  __T.inf={INFO:{1:{t:T-1000},2:{t:T+20*60000}}};notify();uid='%s';pos={lat:47.07,lng:15.44};lastFix=T;0})()"""
with app(width=412,height=915) as (pg,ev,errs):
    # 1) Planung
    r=ev("""(async()=>{const o=[];for(let i=0;i<40;i++){code='PLAN';const g={s:Object.assign({},DEF,{dur:30,head:2,infN:i%5+1,mode:'bounty'})};await infPlan(g,1e12);
      const v=__T.inf.PLAN,ts=Object.values(v).map(x=>x.t).sort((a,b)=>a-b),N=ts.length,T=30*6e4,R0=1e12+2*6e4;
      o.push([N,(ts[0]-R0)/T,(ts[N-1]-R0)/T,Math.min(...ts.slice(1).map((x,j)=>x-ts[j]),1e15)/(.8*T/(N+1))])}return o})()""")
    bad=[x for x in r if x[1]<.2-1e-6 or x[2]>.8+1e-6 or (x[0]>1 and x[0]<4 and x[3]<1-1e-6)]
    print('Planung (N, früh, spät, Abstand/Mindest):',r[:5],'Fehler:',bad);assert not bad and all(x[0]==(i%5+1) for i,x in enumerate(r))
    b=ev("[2,3,4].map(n=>balCalc(Object.assign({},DEF,PRE[30],{dur:30,mode:'bounty',tN:n}),n*2,4,2).o.infN)");print('Balancing infN für 2/3/4 Teams:',b);assert b==[1,2,2]
    # 2) Erscheinen beim Hunter u0 (Team 1)
    ev(SET%(json.dumps(players()),'u0'));ev("join('INFO')");pg.wait_for_timeout(1500)
    for _ in range(20):
        if ev("__T.inf.INFO[1].lat!=null"):break
        pg.wait_for_timeout(300)
    x=ev("__T.inf.INFO[1]");print('Informant 1:',x)
    assert x.get('lat') is not None and ev("D(G.c,__T.inf.INFO[1])<=Rad(G,now())") and ev("__T.inf.INFO[2].lat==null")
    pg.wait_for_timeout(400);print('Marker:',ev("document.querySelectorAll('.mkw').length"),'Infos:',ev("Object.keys(INF)"))
    assert ev("infCode")=='INFO'
    # Hider: kein Listener
    ev("uid='u6';infSync()");print('Hider infCode:',ev("infCode"),'INF:',ev("JSON.stringify(INF)"));assert ev("infCode")==None and ev("JSON.stringify(INF)")=='{}'
    ev("uid='u0';infSync()");pg.wait_for_timeout(400);ev("typeof bfClose==='function'&&bfClose()")
    # 3) Treffen: u0 weit weg → kein Knopf; in 30 m → Knopf, Treffen, Wahl Abhören
    ev("pos={lat:G.c.lat+.01,lng:G.c.lng};panel(1)");assert 'if:1' not in ev("JSON.stringify(infItems(G,now()))")
    ev("pos={lat:__T.inf.INFO[1].lat,lng:__T.inf.INFO[1].lng};panel(1)");pg.wait_for_timeout(200)
    it=ev("JSON.stringify(infItems(G,now()))");print('Panel:',it);assert 'if:1' in it
    ev("gdShow('if:1')");pg.wait_for_timeout(200);shot(pg,'informant_treffen.png');assert 'Informant treffen' in ev("$('gd').innerText")
    ev("infClaim('1')");pg.wait_for_timeout(500);x=ev("__T.inf.INFO[1]");print('nach Treffen:',x);assert x['by']=='u0' and x['tm']==1
    shot(pg,'informant_wahl.png');assert 'Störsender' in ev("$('gd').innerText")
    # zweiter Hunter (Team 2) kann nicht mehr treffen: kein Knopf
    ev("uid='u1';panel(1)");assert 'if:1' not in ev("JSON.stringify(infItems(G,now()))");ev("uid='u0'")
    # Abhören: vorher sieht u0 nur Team 1 (u3), danach alle anderen Hunter
    m0=ev("document.querySelectorAll('.mkw.hunter').length")
    ev("infPick('1','ab')");pg.wait_for_timeout(400);ev("infUse('1')");pg.wait_for_timeout(600);ev("draw()");pg.wait_for_timeout(200)
    print('Abhören aktiv:',ev("infAb(G,now(),1)"),'Team 2:',ev("infAb(G,now(),2)"))
    assert ev("infAb(G,now(),1)") and not ev("infAb(G,now(),2)")
    ab=ev("document.querySelectorAll('.mkw.hunter').length")
    print('Hunter-Marker vorher/nachher:',m0,ab);assert ab-m0==4
    shot(pg,'informant_abhoeren.png')
    # Störsender: Informant 2 erscheint, u1 (Team 2) holt ihn und stört Team 3
    ev("__T.inf.INFO[2]={t:now()-1000,lat:47.071,lng:15.441,by:'u1',tm:2,at:now(),b:'st',u:now(),tg:3};notify()");pg.wait_for_timeout(300)
    j=ev("(()=>{const g=G,t=now(),pk=pgK(g,t);return [infJam(g,pk.next,3),infJam(g,pk.next,1),infJam(g,pk.next,2),infJam(g,pk.next+pk.iv,3)]})()")
    print('Verzögerung nächster Ping Team 3/1/2, übernächster Team 3:',j);assert j==[30000,0,0,0]
    # zweiter Störsender gegen Team 3 → übernächster Ping
    ev("__T.inf.INFO[3]={t:now()-1000,lat:47.071,lng:15.441,by:'u4',tm:2,at:now(),b:'st',u:now()+1,tg:3};notify()");pg.wait_for_timeout(300)
    j=ev("(()=>{const g=G,t=now(),pk=pgK(g,t);return [infJam(g,pk.next,3),infJam(g,pk.next+pk.iv,3)]})()");print('zwei Störsender:',j);assert j==[30000,30000]
    # Ping-Block beim Ziel-Team: Hunter u2 (Team 3) zum Ping-Zeitpunkt → Störungsmeldung, kein Ping
    ev("uid='u2';pos={lat:47.07,lng:15.44};lastK=-1;ping=null");
    k=ev("(()=>{const pk=pgK(G,now());return pk.next-now()})()");pg.wait_for_timeout(int(k)+1500)
    print('Toast Team 3:',ev("$('toast').innerText"),'ping:',ev("!!ping"));assert 'Funk gestört' in ev("$('toast').innerText") and not ev("!!ping")
    print('HUD:',ev("$('hud').innerText"))
    # Replay: Ereignisse aus dem Log
    r=ev("""(()=>{const T=1e12,f={code:'X',round:0,game:{s:Object.assign({},DEF,{mode:'bounty',tN:3,ping:60}),teams:{2:{name:'Füchse'}}},log:[[T,'inf/1/t',T],[T+5,'inf/1/lat',47],[T+5,'inf/1/lng',15],
      [T+9,'inf/1/by','u1'],[T+9,'inf/1/tm',2],[T+9,'inf/1/at',T+9],[T+12,'inf/1/b','st'],[T+20,'inf/1/u',T+20],[T+20,'inf/1/tg',1]]};
      const P_={u1:{id:'u1',name:'Bert',role:'hunter',tm:2}};return rvScan(f,P_).ev.map(e=>[e.t-T,e.x,e.sd.join()])})()""")
    print('Replay-Ereignisse:',r);assert [x[0] for x in r]==[5,9,20] and 'Füchse' in r[1][1] and 'Agentur 1' in r[2][1] and r[2][2]=='t2,t1'
    e1=errs[:]
print('errors:',e1)
sys.exit(1 if e1 else 0)
