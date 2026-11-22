# Test: Lagebericht/Log (KONZEPT_Log.md, Seitenleiste C)
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app(width=412,height=915) as (pg,ev,errs):
    ev("""(()=>{const T=Date.now();__T['.info']={connected:true};const pl={
      u0:{name:'Manuel',role:'hunter',tm:1,tj:1,state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:T},u1:{name:'Tobias',role:'hunter',tm:2,tj:2,state:'alive',j:2,col:0,lat:47.071,lng:15.441,ts:T},
      u2:{name:'Lena',role:'hider',state:'alive',j:3,col:6,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Felix',role:'hider',state:'caught',sT:T-3*6e4,j:4,col:3,lat:47.069,lng:15.439,ts:T}};
      __T.games={LOGT:{host:'u0',status:'running',startAt:T-12*6e4,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:2,head:1}),players:pl,
        teams:{1:{name:'Die Füchse',col:10},2:{name:'Schattenkartell',col:11}},catches:{u3:{hunter:'u1',t:T-3*6e4,status:'done',lat:47.069,lng:15.439}},
        ev:{e1:{t:T-3*6e4,x:'Tobias fängt Felix',u:'u1'},e2:{t:T-8*6e4,x:'Zone schrumpft: jetzt 500 m',u:'x'}}}};notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=T})()""")
    ev("join('LOGT')");pg.wait_for_timeout(1500);ev("bfClose&&bfClose()")
    # Knopf wie Chat-Knopf
    sz=ev("(()=>{const a=$('lgk').getBoundingClientRect(),b=$('cb').getBoundingClientRect(),ca=getComputedStyle($('lgk')),cb=getComputedStyle($('cb'));return[a.width,a.height,b.width,b.height,ca.borderRadius,cb.borderRadius,ca.backgroundColor===cb.backgroundColor,a.right===b.right,getComputedStyle($('lgk')).display]})()")
    print('Knopf:',sz);assert sz[0]==sz[2] and sz[1]==sz[3] and sz[4]==sz[5] and sz[6] and sz[7] and sz[8]=='grid'
    # Einträge
    ev("blRef={p:[['u2',47.0705,15.4405]]};toast('📡 Ping!')");ev("toast('Kopiert')");ev("toast('Lena hat das Signal verloren')");ev("toast('Lena hat das Signal verloren')")
    pg.wait_for_timeout(200)
    a=ev("BL.a.map(e=>e.x+(e.n>1?' ×'+e.n:''))");print('Log:',a)
    assert a[0]=='Lena hat das Signal verloren ×2' and a[1]=='Ping!' and not any('Kopiert' in x for x in a)
    assert ev("$('lgk').classList.contains('new')")
    ev("blToggle()");pg.wait_for_timeout(400)
    rows=ev("[...document.querySelectorAll('#blg .blr')].map(r=>r.innerText.replace(/\\n/g,' '))");print('Verlauf:',rows)
    assert any('fängt Felix' in r and 'zeigen' in r for r in rows) and any('Zone schrumpft' in r for r in rows) and any('Ping!' in r and 'Karte' in r for r in rows)
    assert not ev("$('lgk').classList.contains('new')")
    shot(pg,'lagebericht_verlauf.png')
    ev("blF='catch';blRender()");assert ev("document.querySelectorAll('#blg .blr').length")==1;ev("blF='all';blRender()")
    ev("blTab='l';blRender()");pg.wait_for_timeout(300)
    t=ev("$('blg').innerText");print('Lage:',t.replace('\n',' | ')[:400])
    assert 'Die Füchse' in t and 'Schattenkartell' in t and '1 / 2 FREI' in t.upper() and 'Tobias' in t and 'Restzeit' in t
    shot(pg,'lagebericht_lage.png')
    # Ping antippen → Positionen auf der Karte
    ev("blTab='v';blRender()");ev("blGo(BL.a.findIndex(e=>e.r))");pg.wait_for_timeout(400)
    assert ev("!!blShowL&&blShowL.getLayers().length")==2 and not ev("blOpen")
    print('Ping-Etikett:',ev("document.querySelector('.blpt').innerText"))
    shot(pg,'lagebericht_ping.png')
    # Fang antippen → Handschellen
    ev("blClear();blGo(BL.a.findIndex(e=>/fängt Felix/.test(e.x)))");pg.wait_for_timeout(300)
    assert ev("blShowL.getLayers().length")==1
    # Neue Runde → leer
    ev("__T.games.LOGT.rn=1;notify()");pg.wait_for_timeout(300)
    assert ev("blLoad().a.length")==0 and not any(k.startswith('blog_LOGT_0') for k in ev("Object.keys(LS)"))
    print('errors:',errs[:5]);assert not errs
