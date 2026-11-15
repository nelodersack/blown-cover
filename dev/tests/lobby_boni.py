# Test: Lobby-Unterseite „Boni“ (Symbole wie im Spiel + Einstellbereich darunter) und Belohnungs-Hinweise unter Aufgaben
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:120,pen:1,mode:'survive',taskR:0,imm:120,shOn:true,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:40,hbT:15,gw:20,gd:60,ot:3},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0706,lng:15.4406,ts:T}},cols:{0:'u1',1:'u2',2:'u3'}}};
      uid='u1';pos={lat:47.069,lng:15.4385};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("window.__k=setInterval(()=>{const p=__T.games.K7QF.players;for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},500)")
    ev("tabGo('lt','set')");ev("ui.sub='tasks';panel(1)")
    ev("G.s.ddN=1;__T.games.K7QF.s.ddN=1;__T.games.K7QF.s.mtN=1;notify()");pg.wait_for_timeout(500)
    ev("$('panel').classList.remove('m')")
    pb=ev("$('pb').innerText");
    assert 'Belohnung: Satellitenbild und Hunter-Radar' in pb and 'Belohnung: jeder wählt Hunter-Radar' in pb and 'Belohnung: Immunität für Platz 1 und 2' in pb, pb[:900]
    ev("ui.sub='bon';panel(1)");pg.wait_for_timeout(300);pb=ev("$('pb').innerText")
    assert 'Hunter-Boni' in pb and 'Satellitenbild-Dauer' not in pb and 'Radar-Radius' not in pb
    tiles=ev("[...document.querySelectorAll('.mzi')].map(b=>b.querySelector('b').innerText+'|'+b.classList.contains('off'))");print(tiles)
    assert len(tiles)==6 and all(t.endswith('false') for t in tiles)
    shot(pg,'lobby_boni.png')
    # Antippen öffnet den Einstellbereich direkt darunter
    ev("[...document.querySelectorAll('.mzi')].find(b=>/Hider-Radar/.test(b.textContent)).click()");pg.wait_for_timeout(300)
    dt=ev("document.querySelector('.mzsh').innerText");print(dt.replace('\n',' | '));assert 'Radius' in dt and 'Dauer' in dt and 'Hider-Radar kommt nach' in dt
    shot(pg,'lobby_boni_radar.png')
    ev("stp('bmR',1)");pg.wait_for_timeout(500)
    assert ev("__T.games.K7QF.s.bmR")==5 and '5 m' in ev("[...document.querySelectorAll('.mzi')].find(b=>/Hunter-Radar/.test(b.textContent)).innerText")
    # Hunter-Boni aus: Symbole grau, Vorrat-Satz verschwindet
    ev("__T.games.K7QF.s.hbOn=false;notify()");pg.wait_for_timeout(400)
    assert ev("[...document.querySelectorAll('.mzi')].find(b=>/Live/.test(b.textContent)).classList.contains('off')") and 'Vorrat' not in ev("$('pb').innerText")
    ev("edGo('b:live')");pg.wait_for_timeout(200);assert 'Nicht im Spiel' in ev("document.querySelector('.mzsh').innerText")
    ev("__T.games.K7QF.s.hbOn=true;notify()");pg.wait_for_timeout(400);assert 'Vorrat' in ev("$('pb').innerText")
    # Satellitenbild ohne Aufgaben-Belohnung: Modus Mission, bon aus
    ev("__T.games.K7QF.s.mode='mission';__T.games.K7QF.s.bon=false;notify()");pg.wait_for_timeout(400)
    ev("ui.ed=null;edGo('b:sat')");pg.wait_for_timeout(200)
    assert 'Aufgaben-Belohnungen sind aus' in ev("document.querySelector('.mzsh').innerText")
    print('errors:',errs[:5]);assert not [e for e in errs if 'PE:' in e]
