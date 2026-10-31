# Test: Replay-Zeitleiste „Lupe“ (Übersicht + Detailspur), Wischen/Tippen in der Detailspur, Filter-Chips
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot,OUT
def load(ev,dur,ping,shrink):
    ev("""(()=>{G=null;code=null;if(RV)rvClose();
      const T0=1800000000000,R0=T0+120000,s={r0:1500,rMin:600,shrink:%d,step:75,head:2,dur:%d,ping:%d,pen:2,mode:'survive',imm:120,bon:true,hbC:60,hbL:60};
      const pl=[{id:'u1',name:'Anna',role:'hunter',col:0,j:1,state:'alive'},{id:'u2',name:'Lena',role:'hider',col:1,j:2,state:'alive'}];
      const tr={u1:[],u2:[]};for(let t=T0;t<=R0+%d*60000;t+=30000){tr.u1.push([t,47.069,15.4385,10]);tr.u2.push([t,47.0705,15.4405,10])}
      const log=[];for(let m=3;m<%d;m+=7){const t=R0+m*60000;log.push([t,'tasks/sh/t0',t],[t,'tasks/sh/loc/lat',47.07],[t,'tasks/sh/loc/lng',15.44]);log.push([t+90000,'tasks/sh/in/u2/t',t+90000])}
      rvLoad({format:'blown-cover-replay',v:2,code:'TEST',round:0,game:{s,c:{lat:47.07,lng:15.44},startAt:T0,R0,end:R0+%d*60000,winner:'hider'},players:pl,tracks:tr,log})})()"""%(shrink,dur,ping,dur,dur,dur))
with app() as (pg,ev,errs):
    for dur,ping,shrink in ((30,150,3),(120,300,6)):
        load(ev,dur,ping,shrink);pg.wait_for_timeout(500)
        ev("RV.t=RV.f.game.R0+%d*60000;rvDraw()"%(dur*0.42))
        w=ev("rvWin()/60000");box=ev("(()=>{const r=$('rvD').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()")
        print(dur,'Min: Lupe',w,'Min · Fenster',ev("$('rvW').style.left+' / '+$('rvW').style.width"),'· Abspielkopf',ev("$('rvP').style.left"))
        print('  Detail: pg',ev("document.querySelectorAll('#rvS .pg').length"),'zs',ev("document.querySelectorAll('#rvS .zs').length"),'ev',ev("document.querySelectorAll('#rvS .ev').length"),'Labels',ev("[...document.querySelectorAll('#rvS .lb')].length"))
        pg.locator('#panel').screenshot(path=OUT+'/zeitleiste_lupe_%d.png'%dur)
        # Wischen um 1/4 der Breite nach links = 1/4 Fenster vorwärts
        t0=ev("RV.t");x,y=box[0]+box[2]/2,box[1]+box[3]/2
        pg.mouse.move(x,y);pg.mouse.down();pg.mouse.move(x-box[2]/4,y,steps=6);pg.mouse.up();pg.wait_for_timeout(100)
        print('  Wischen: +%.1f s (erwartet %.1f)'%((ev("RV.t")-t0)/1000,w*60/4))
        # Tippen ganz rechts in der Detailspur
        t1=ev("RV.t");a=ev("rvWA(RV.t)");pg.mouse.click(box[0]+box[2]-2,y);pg.wait_for_timeout(100)
        print('  Tippen rechts: Zeit im Fenster',round((ev("RV.t")-a)/60000,2),'von',w)
    # Filter-Chips (nur Fang, Knapp!, Aufgabe, Bonus)
    ev("RV.play=false");print('Chips:',ev("[...document.querySelectorAll('.rvch .chip')].map(c=>c.innerText).join(' | ')"))
    n0=ev("document.querySelectorAll('#rvS .ev').length")
    pg.locator('.rvch .chip',has_text='Aufgabe').click();pg.wait_for_timeout(200)
    print('Aufgabe aus: ev',n0,'->',ev("document.querySelectorAll('#rvS .ev').length"),'off:',ev("document.querySelector('.rvch .chip.off').innerText"))
    pg.locator('.rvch .chip',has_text='Aufgabe').click();pg.wait_for_timeout(200)
    print('wieder an:',ev("document.querySelectorAll('#rvS .ev').length"))
    print('errors:',errs[:8])
