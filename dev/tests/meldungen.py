# Test: Meldungen (Manuel 21.11.): im Spiel Konzept B (Stapel bis 3 Zeilen, Farbe nach Art), im Replay Konzept C
# (Ereignis mit Ort → Etikett auf der Karte, ohne Ort → Pille oben)
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app(width=412,height=915) as (pg,ev,errs):
    ev("""(()=>{const T=Date.now();__T['.info']={connected:true};const pl={u0:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:T},u1:{name:'Lena',role:'hider',state:'alive',j:2,col:3,lat:47.071,lng:15.441,ts:T}};
      __T.games={MELD:{host:'u0',status:'running',startAt:T-5*6e4,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{head:0}),players:pl}};notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=T})()""")
    ev("join('MELD')");pg.wait_for_timeout(1200);ev("bfClose&&bfClose()")
    for m in ['Ping: Hider-Positionen','Lena setzt Extra-Ping ein','Anna fängt Lena','Lena erreicht das Safehouse']: ev("toast(%s)"%json.dumps(m))
    pg.wait_for_timeout(300)
    rows=ev("[...document.querySelectorAll('#toast .t')].map(d=>d.innerText+'|'+d.style.getPropertyValue('--c'))");print('Stapel:',rows)
    assert len(rows)==3 and rows[0].startswith('Lena erreicht') and '#7c6cff' in rows[0] and '#e5484d' in rows[1] and '#4fb3f0' in rows[2]
    shot(pg,'meldungen_spiel.png')
    # Replay
    T0=1800000000000;R0=T0+60000
    tr={'p1':[[T0+i*5000,47.07,15.44+i*1e-5,8] for i in range(400)],'p2':[[T0+i*5000,47.0705,15.4405,8] for i in range(400)]}
    f={'format':'blown-cover-replay','v':2,'code':'MELD','round':0,'game':{'s':ev("Object.assign({},DEF,preOf(30),{head:1,ping:120})"),'c':{'lat':47.07,'lng':15.44},'startAt':T0,'R0':R0,'end':R0+30*60000,'winner':'hunter'},
       'players':[{'id':'p1','name':'Anna','role':'hunter','col':0,'state':'alive'},{'id':'p2','name':'Lena','role':'hider','col':3,'state':'alive'}],'tracks':tr,
       'log':[[R0+5*60000,'catches/p2/hunter','p1'],[R0+5*60000,'players/p2/state','caught'],[R0+5*60000,'players/p2/sT',R0+5*60000]]}
    ev("rvClose&&RV&&rvClose();G=null;code=null");pg.evaluate('f=>rvLoad(f)',f);pg.wait_for_timeout(2200)
    ev("RV.t=%d;RV.speed=50;rvPlay()"%(R0+4*60000+50000));pg.wait_for_timeout(1600)
    n=ev("[...document.querySelectorAll('.rvn')].map(e=>e.innerText)");pill=ev("($('rvpill')||{}).innerText||''")
    print('Etiketten:',n,'Pille:',pill,'Toasts:',ev("document.querySelectorAll('#toast .t').length"))
    assert any(x.strip().endswith('Fang!') for x in n) and not any('fängt' in x for x in n) and 'Ping' in pill
    assert ev("RV.ev.some(e=>e.ti==='Fang!'&&/fängt Lena/.test(e.x))")   # Titel auf der Karte, ausführlich im Panel
    ev("RV.play=false");shot(pg,'meldungen_replay.png')
    print('errors:',errs[:5]);assert not errs
