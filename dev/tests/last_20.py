# Test: 20 Spieler (Geburtstagsrunde). 1) Farben: 20 Spieler bekommen in der Lobby automatisch eine Farbe; ab 13 teilen sich je zwei
# eine Farbe, Farbe+Buchstabe(n) bleiben eindeutig (gleicher Anfangsbuchstabe → zwei Buchstaben). 2) Belastung: laufendes Spiel mit
# 6 bzw. 20 Spielern, jeder schreibt alle 4 s seinen Standort (wie write()), CPU 4× gebremst (Mittelklasse-Handy); gemessen werden
# Rechenzeit je Datenbank-Update (onData inkl. draw/panel) und lange Aufgaben (> 50 ms). Ausgabe als Tabelle, Grenze siehe LIM.
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
NAMES=['Anna','Lena','Max','Tom','Mia','Paul','Lisa','Felix','Sara','Jonas','Eva','Lukas','Marie','Leon','Tina','Moritz','Laura','Ben','Mara','Theo']
LIM=float(os.environ.get('LIM','60'))   # ms je Update bei 4× gebremster CPU (Update kommt bei 20 Spielern alle ~200 ms)
def setup(n,status,me,role_me):
    pl={}
    for i in range(n):
        u='u%d'%i;r='hunter' if i<max(1,round(n/4)) else 'hider'
        pl[u]={'name':NAMES[i],'role':r,'state':'alive','j':i+1,'lat':47.07+((i*37)%19-9)*4e-4,'lng':15.44+((i*53)%23-11)*5e-4,'ts':0}
    if role_me=='spec':pl[me]={'name':'Zuschauer','role':'spec','state':'spec','j':99}
    return json.dumps(pl)
COL="""(async()=>{const T=Date.now();__T['.info']={connected:true};
  __T.games={GEBX:{host:'u0',status:'lobby',c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(60),{mode:'survive'}),players:%s}};
  for(const k in __T.games.GEBX.players)__T.games.GEBX.players[k].ts=T;notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=T;0})()"""
with app(width=412,height=915) as (pg,ev,errs):
    ev(COL%setup(20,'lobby','u0','hunter'));ev("join('GEBX')");pg.wait_for_timeout(800)
    for i in range(20):
        ev("(async()=>{uid='u%d';G=__T.games.GEBX;await autoCol();notify()})()"%i);pg.wait_for_timeout(60)
    pg.wait_for_timeout(400);ev("uid='u0'")
    res=ev("Object.keys(P()).map(k=>[P()[k].name,P()[k].col,colI(k),letOf(k)])")
    print('farben:',' '.join('%s:%s/%s%s'%(n,c,ci,l) for n,c,ci,l in res))
    keys=['%s|%s'%(ci,l) for n,c,ci,l in res]
    assert all(isinstance(c,int) for n,c,ci,l in res) and len(set(c for n,c,ci,l in res))==20, 'jeder braucht einen eigenen Platz'
    assert len(set(keys))==20, 'Farbe+Buchstabe muss eindeutig sein: %s'%keys
    # gleicher Anfangsbuchstabe in derselben Farbe (von Hand gewählt): Max (Platz 2) und Mara/Marie → mehrere Buchstaben
    ev("__T.games.GEBX.players.u18.col=14;notify()");pg.wait_for_timeout(300)
    lt=ev("[letOf('u2'),letOf('u18')]");print('gleiche Farbe, gleicher Anfang:',lt);assert lt[0]!=lt[1] and lt[0].startswith('M'),lt
    ev("ui.pal=1;panel(1)");pg.wait_for_timeout(300);shot(pg,'last20_farben.png')
    e0=errs[:]

RUN="""(()=>{const T=Date.now();__T['.info']={connected:true};const pl=%s;let c=0;for(const k in pl){pl[k].ts=T;if(pl[k].role!=='spec')pl[k].col=c++}
  __T.games={GEBY:{host:'u0',status:'running',startAt:T-300000,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(60),{mode:'survive',head:0,dq:false}),players:pl}};
  notify();uid='%s';pos=pl['%s'].lat?{lat:pl['%s'].lat,lng:pl['%s'].lng}:{lat:47.07,lng:15.44};lastFix=T;0})()"""
MEAS="""(()=>{window.__m=[];window.__lt=[];const o=onData;onData=function(){const t=performance.now();const r=o.apply(this,arguments);__m.push(performance.now()-t);return r};
  try{new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(e.duration))).observe({type:'longtask'})}catch(e){}
  const ids=Object.keys(__T.games.GEBY.players).filter(k=>k!==uid&&__T.games.GEBY.players[k].role!=='spec');let i=0;
  window.__w=setInterval(()=>{const k=ids[i++%ids.length],p=__T.games.GEBY.players[k];p.lat+=(Math.random()-.5)*6e-5;p.lng+=(Math.random()-.5)*8e-5;p.ts=Date.now();
    lastFix=Date.now();notify()},4000/ids.length);0})()"""
rows=[];el=[]
for n,role,me in [(6,'hunter','u0'),(20,'hunter','u0'),(6,'hider','u3'),(20,'hider','u9'),(20,'spec','sx')]:
    with app(width=412,height=915) as (pg,ev,errs):
        ev(RUN%(setup(n,'running',me,role),me,me,me,me));ev("join('GEBY')");pg.wait_for_timeout(1200)
        cdp=pg.context.new_cdp_session(pg);cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
        ev(MEAS);pg.wait_for_timeout(20000);ev("clearInterval(__w)")
        m=ev("__m.slice().sort((a,b)=>a-b)");lt=ev("__lt")
        k=len(m);avg=sum(m)/k;p95=m[int(k*.95)];busy=sum(m)/20000*100
        rows.append((n,role,k,avg,p95,max(m),busy,len(lt)))
        if n==20 and role=='hunter':shot(pg,'last20_karte.png')
        el+=errs[:]
print('\nSpieler Rolle     Updates  Ø ms   95% ms  max ms  CPU-Anteil  >50ms')
for n,r,k,a,p,mx,b,l in rows:print('%7d %-9s %7d %6.1f %8.1f %7.1f %9.0f %%  %5d'%(n,r,k,a,p,mx,b,l))
for n,r,k,a,p,mx,b,l in rows:assert p<LIM,'%d %s: 95%%-Wert %.0f ms über %d ms'%(n,r,p,LIM)
print('errors:',e0+[e for e in el if 'longtask' not in e][:8])
