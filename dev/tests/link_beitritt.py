# Test: Einladungslink blowncover.app/CODE (über ?c=CODE), Beitritt als Zuschauer in ein laufendes Spiel,
# geschlossene Lobby, Teilen-Link, neue Runde macht Zuschauer zu Hidern
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
SETUP="""(()=>{__T['.info']={connected:true};notify();const T=Date.now(),b={lat:47.07,lng:15.44};
  const s={r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:600,pen:2,mode:'survive',taskR:0,imm:120,shOn:false,shT:10,evT:5,ddN:0,ddT:5,mtN:0,mtT:5,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:0,rp:true};
  const pl=()=>({u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.069,lng:15.439,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T}});
  __T.games={RUNX:{host:'u1',status:'running',startAt:T-60000,c:b,s,players:pl(),cols:{0:'u1',1:'u2'}},
             LOBX:{host:'u1',status:'lobby',c:b,s,players:pl(),cols:{0:'u1',1:'u2'}},
             OVRX:{host:'u1',status:'over',winner:'hider',startAt:T-4e6,c:b,s,players:pl(),cols:{0:'u1',1:'u2'}}};
  uid='u9';pos={lat:47.0702,lng:15.4402};lastFix=Date.now()})()"""
TXT="document.getElementById('pb').innerText.replace(/\\n/g,' | ').slice(0,300)"

# 1) Link auf ein laufendes Spiel → Einladung, dann Zuschauer
with app(hash='?c=runx#test') as (pg,ev,errs):
    ev(SETUP);ev("panel(1)");pg.wait_for_timeout(300)
    print('linkc:',ev("LINKC"),'url:',ev("location.search+'|'+location.hash"))
    print('start:',ev(TXT))
    shot(pg,'link_einladung.png')
    ev("document.getElementById('nm').value='Gast'");ev("jn()");pg.wait_for_timeout(1500)
    me=ev("JSON.stringify(__T.games.RUNX.players.u9)");print('me:',me)
    assert '"role":"spec"' in me and '"state":"spec"' in me and 'lat' not in me
    print('panel:',ev(TXT))
    assert 'Du schaust zu' in ev(TXT)
    ev("write(true)");pg.wait_for_timeout(400)
    print('nach write lat?', ev("__T.games.RUNX.players.u9.lat"))
    assert ev("__T.games.RUNX.players.u9.lat")is None
    print('res ohne Zuschauer:',ev("buildRes(G).l.map(x=>x.n).join(',')"))
    assert 'Gast' not in ev("buildRes(G).l.map(x=>x.n).join(',')")
    print('snap:',ev("Object.keys(rpSnap(G)).join(',')"))
    shot(pg,'link_zuschauer.png')
    # Spielende und neue Runde: Zuschauer wird Hider
    ev("__T.games.RUNX.status='over';__T.games.RUNX.winner='hider';notify()");pg.wait_for_timeout(500)
    ev("uid='u1';newRound()");pg.wait_for_timeout(500)
    print('neue Runde:',ev("JSON.stringify(__T.games.RUNX.players.u9)"))
    assert '"role":"hider"' in ev("JSON.stringify(__T.games.RUNX.players.u9)")
    print('errors:',errs[:8]); err1=[e for e in errs if 'PE:' in e]

# 2) Lobby, geschlossene Lobby, unbekannter Code, Teilen-Link
with app(hash='?c=OVRX#test') as (pg,ev,errs):
    ev(SETUP);ev("panel(1)");pg.wait_for_timeout(300)
    ev("jn()");pg.wait_for_timeout(1200)
    print('over:',ev("document.getElementById('toast').innerText"),'| G?',ev("!!G"),'| start:',ev(TXT)[:80])
    assert ev("!G") and 'geschlossen' in ev("document.getElementById('toast').innerText") and 'eingeladen' not in ev(TXT)
    ev("document.getElementById('cd').value='ZZZZ';jn()");pg.wait_for_timeout(1200)
    print('unbekannt:',ev("document.getElementById('toast').innerText"))
    assert 'nicht gefunden' in ev("document.getElementById('toast').innerText")
    ev("document.getElementById('cd').value='LOBX';jn()");pg.wait_for_timeout(1500)
    print('lobby:',ev("JSON.stringify(__T.games.LOBX.players.u9)"))
    assert '"role":"hider"' in ev("JSON.stringify(__T.games.LOBX.players.u9)")
    print('link:',ev("LINK(code)"))
    assert ev("LINK(code)")=='https://blowncover.app/LOBX'
    ev("navigator.share=o=>{window.__sh=o;return Promise.resolve()};shCode()")
    print('geteilt:',ev("JSON.stringify(window.__sh)"))
    assert ev("window.__sh.url")=='https://blowncover.app/LOBX'
    print('ungültiger Link ignoriert:',ev("(()=>{return /^[A-Za-z2-9]{4,6}$/.test('../x')})()"))
    print('errors:',errs[:8]+err1)
