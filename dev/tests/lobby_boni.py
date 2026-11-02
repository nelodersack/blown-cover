# Test: Lobby-Bereich „Boni“ (Kacheln + Fenster zum Einstellen) und Belohnungs-Hinweise unter Aufgaben
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:120,pen:1,mode:'survive',taskR:0,imm:120,shOn:true,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:40,hbT:15,gw:20,gd:60,ot:3},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T}},cols:{0:'u1',1:'u2',2:'u3'}}};
      uid='u1';pos={lat:47.069,lng:15.4385};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},500)")
    ev("tabGo('lt','set')");ev("ui.adv=true;ui.open.tasks=1;ui.open.bon=1;panel(1)")
    ev("G.s.ddN=1;__T.games.K7QF.s.ddN=1;__T.games.K7QF.s.mtN=1;notify()");pg.wait_for_timeout(500)
    ev("$('panel').classList.remove('m')")
    pb=ev("$('pb').innerText");
    assert 'Belohnung: Satellitenbild und Hunter-Radar' in pb and 'Belohnung: jeder wählt Hunter-Radar' in pb and 'Belohnung: Immunität für Platz 1 und 2' in pb, pb[:900]
    assert 'Hunter-Boni' in pb and 'Satellitenbild-Dauer' not in pb and 'Radar-Radius' not in pb
    tiles=ev("[...document.querySelectorAll('.bnt')].map(b=>b.querySelector('b').innerText+'|'+b.classList.contains('off'))");print(tiles)
    assert len(tiles)==5 and all(t.endswith('false') for t in tiles)
    ev("document.querySelector('.bnt.wide').scrollIntoView({block:'center'})");pg.wait_for_timeout(200);shot(pg,'lobby_boni.png')
    ev("[...document.querySelectorAll('.bnt')].find(b=>/Radar/.test(b.textContent)).click()");pg.wait_for_timeout(300)
    dt=ev("$('bnd').innerText");print(dt.replace('\n',' | '));assert 'Radius' in dt and 'Dauer' in dt and 'Hider-Radar kommt nach' in dt
    shot(pg,'lobby_boni_radar.png')
    ev("stp('bmR',1)");pg.wait_for_timeout(500)
    assert ev("__T.games.K7QF.s.bmR")==5 and ev("$('bnd').querySelector('input').value")=='5'
    assert '5 m' in ev("document.querySelector('.bnt.wide').innerText")
    pg.keyboard.press('Escape');pg.wait_for_timeout(200);assert not ev("!!$('bnd')")
    # Hunter-Boni aus: Kacheln grau, Fenster zeigt Grund
    ev("__T.games.K7QF.s.hbOn=false;notify()");pg.wait_for_timeout(400)
    assert 'Nicht im Spiel' in ev("[...document.querySelectorAll('.bnt')].find(b=>/Live/.test(b.textContent)).textContent")
    ev("bnShow('hb')");pg.wait_for_timeout(200);assert 'Vorrat' not in ev("$('bnd').innerText")
    ev("__T.games.K7QF.s.hbOn=true;notify()");pg.wait_for_timeout(400);assert 'Vorrat' in ev("$('bnd').innerText")
    ev("bnClose()")
    # Satellitenbild ohne Aufgaben-Belohnung: Modus Mission, bon aus
    ev("__T.games.K7QF.s.mode='mission';__T.games.K7QF.s.bon=false;notify()");pg.wait_for_timeout(400)
    assert 'Aufgaben-Belohnungen sind aus' in ev("[...document.querySelectorAll('.bnt')].find(b=>/Satelliten/.test(b.textContent)).textContent")
    # Spielstart schließt Fenster
    ev("bnShow('imm');__T.games.K7QF.status='running';__T.games.K7QF.startAt=Date.now();notify()");pg.wait_for_timeout(600);assert not ev("!!$('bnd')")
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
