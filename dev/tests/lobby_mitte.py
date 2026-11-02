# Test: Lobby-Panel startet in der Zwischenstufe (bis unter „Balancing“), rastet ganz/Mitte/unten ein
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:120,pen:1,mode:'survive',taskR:0,imm:120,shOn:true,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:40,hbT:15,gw:20,gd:60,ot:3},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T}},cols:{0:'u1',1:'u2'}}};
      uid='u1';pos={lat:47.069,lng:15.4385};lastFix=Date.now()})()""")
    ev("join('K7QF')");pg.wait_for_timeout(600)
    ev("tabGo('lt','set')");pg.wait_for_timeout(400)
    st=lambda:ev("(()=>{const P=$('panel'),a=$('pb').querySelector('[data-mid]').getBoundingClientRect(),r=P.getBoundingClientRect();return {m:P.classList.contains('m'),c:P.classList.contains('c'),mid:P.style.getPropertyValue('--mid'),vis:Math.round(innerHeight-r.top),gap:Math.round(innerHeight-a.bottom)}})()")
    s=st();print('Start',s);assert s['m'] and not s['c'] and int(s['mid'][:-2])>40 and 6<=s['gap']<=18,s
    shot(pg,'lobby_mitte.png')
    # Scrollen in der Mitte bis ganz unten möglich: letzter Knopf sichtbar
    ev("$('ps').scrollTop=1e5");pg.wait_for_timeout(200)
    vb=ev("(()=>{const b=[...$('pf').querySelectorAll('button')].pop().getBoundingClientRect();return Math.round(innerHeight-b.bottom)})()");print('Knopf unten Abstand',vb);assert vb>=0
    ev("$('ps').scrollTop=0")
    tap=lambda:(pg.locator('#ph').click(),pg.wait_for_timeout(350))
    tap();s=st();print('Tipp1',s);assert not s['m'] and not s['c']     # Mitte → ganz
    tap();s=st();print('Tipp2',s);assert s['m']                         # ganz → Mitte
    b=pg.locator('#ph').bounding_box();x=b['x']+b['width']/2;y=b['y']+b['height']/2
    pg.mouse.move(x,y);pg.mouse.down();pg.mouse.move(x,y+700,steps=8);pg.mouse.up();pg.wait_for_timeout(350)
    s=st();print('Ziehen runter',s);assert s['c']
    tap();s=st();print('Tipp3',s);assert s['m'] and not s['c']         # unten → Mitte
    b=pg.locator('#ph').bounding_box();y=b['y']+b['height']/2
    pg.mouse.move(x,y);pg.mouse.down();pg.mouse.move(x,max(5,y-600),steps=8);pg.mouse.up();pg.wait_for_timeout(350)
    s=st();print('Ziehen hoch',s);assert not s['m'] and not s['c']
    # gewählte Stufe bleibt bei Neuzeichnen
    ev("panel(1)");s=st();assert not s['m']
    # Spieler-Tab: kein Anker, Versatz 0
    ev("$('panel').classList.add('m');tabGo('lt','players')");pg.wait_for_timeout(300)
    print('Spieler-Tab mid',ev("$('panel').style.getPropertyValue('--mid')"));assert ev("$('panel').style.getPropertyValue('--mid')")=='0px'
    # Regression 02.11.: gescrolltes Menü + Bereich öffnen (z. B. „Boni“) darf das Panel nicht aus dem Bild schieben
    ev("tabGo('lt','set');$('panel').classList.remove('c');$('panel').classList.add('m');pMidSet()");pg.wait_for_timeout(300)
    m0=ev("$('panel').style.getPropertyValue('--mid')")
    ev("ui.adv=true;$('ps').scrollTop=600");pg.wait_for_timeout(200);ev("ui.open.bon=1;panel(1)");pg.wait_for_timeout(600)
    r=ev("[Math.round($('panel').getBoundingClientRect().top),innerHeight,$('panel').style.getPropertyValue('--mid')]");print('gescrollt',r,m0)
    assert r[0]<r[1]-100 and r[2]==m0,r
    ev("ui.open.bon=0;$('ps').scrollTop=0;panel(1)")
    # Spielstart: keine Zwischenstufe
    ev("__T.games.K7QF.status='running';__T.games.K7QF.startAt=Date.now();notify()");pg.wait_for_timeout(500)
    assert not ev("$('panel').classList.contains('m')");print('Spiel läuft: ok')
    print('errors:',errs[:5]);assert not errs
