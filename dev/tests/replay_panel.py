# Test: Replay-Panel mit Zwischenstufe (Standard beim Öffnen), Ziehen/Antippen zwischen voll, Mitte, eingeklappt
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app(width=412,height=915) as (pg,ev,errs):
    ev("""(()=>{const T0=1800000000000,R0=T0+120000,s={r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:180,pen:2,mode:'survive',imm:120,bon:true,hbC:60,hbL:60};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'}];
      const tr={u1:[],u2:[]};for(let t=T0;t<=R0+30*60000;t+=30000){tr.u1.push([t,47.069,15.4385,10]);tr.u2.push([t,47.0705,15.4405,10])}
      rvLoad({format:'blown-cover-replay',v:2,code:'TEST',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+30*60000,winner:'hider'},players:pl,tracks:tr,log:[]})})()""")
    pg.wait_for_timeout(800)
    st=lambda:ev("(()=>{const P=$('panel'),r=P.getBoundingClientRect(),k=document.querySelector('#pb .ctl').getBoundingClientRect();return (P.classList.contains('c')?'c':P.classList.contains('m')?'m':'voll')+' · sichtbar '+Math.round(innerHeight-r.top)+' px · Abspieltasten unten bei '+Math.round(k.bottom)+' / Bild '+innerHeight})()")
    print('Start:',st());shot(pg,'replay_panel_mitte.png')
    # Nachträgliche Höhenänderung (wie in der App: Schriften/Fenster später): Zwischenstufe muss nachziehen
    ev("document.querySelector('#pb h2').style.fontSize='40px'");pg.wait_for_timeout(400);print('nach größerer Überschrift:',st())
    ev("document.querySelector('#pb h2').style.fontSize=''");pg.wait_for_timeout(400);print('zurück:',st())
    pg.set_viewport_size({'width':412,'height':780});pg.wait_for_timeout(600);print('kleineres Fenster:',st())
    pg.set_viewport_size({'width':412,'height':915});pg.wait_for_timeout(600);print('wieder groß:',st())
    ph=ev("(()=>{const r=$('ph').getBoundingClientRect();return[r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.click(*ph);pg.wait_for_timeout(400);print('Tipp:',st())
    pg.mouse.click(*ev("(()=>{const r=$('ph').getBoundingClientRect();return[r.left+r.width/2,r.top+r.height/2]})()"));pg.wait_for_timeout(400);print('Tipp:',st())
    def drag(d):
        x,y=ev("(()=>{const r=$('ph').getBoundingClientRect();return[r.left+r.width/2,r.top+r.height/2]})()")
        pg.mouse.move(x,y);pg.mouse.down();pg.mouse.move(x,y+d,steps=6);pg.mouse.up();pg.wait_for_timeout(400)
    drag(600);print('ganz runter:',st())
    drag(-150);print('etwas hoch:',st())
    drag(-400);print('ganz hoch:',st())
    drag(150);print('zurück in die Mitte:',st())
    # Scrollen in der Mitte: Karte „Statistik“-Tab muss erreichbar werden
    vis=lambda:ev("(()=>{const b=[...document.querySelectorAll('#pb .rvtab button')].pop().getBoundingClientRect();return Math.round(b.bottom)+' / '+innerHeight})()")
    print('Tabs vor dem Scrollen unten bei',vis())
    ev("$('ps').scrollTop=9999");pg.wait_for_timeout(200);print('nach dem Scrollen unten bei',vis(),'· scrollbar:',ev("$('ps').scrollHeight>$('ps').clientHeight"))
    print('Replay schließen erreichbar:',ev("(()=>{const b=document.querySelector('#pf button').getBoundingClientRect();return b.bottom<=innerHeight&&b.top>=$('panel').getBoundingClientRect().top})()"),'· im Scrollbereich:',ev("!!document.querySelector('#ps #pf button')"))
    shot(pg,'replay_panel_gescrollt.png')
    ev("$('ps').scrollTop=0")
    ev("RV.tab='stat';panel(1)");pg.wait_for_timeout(300);print('Statistik:',ev("$('panel').classList.contains('m')"))
    ev("rvClose()");pg.wait_for_timeout(300);print('nach Schließen m:',ev("$('panel').classList.contains('m')"))
    print('errors:',errs[:5])
