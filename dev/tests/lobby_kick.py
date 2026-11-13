# Test: Host entfernt einen Spieler aus der Lobby (Menü beim Antippen), der Entfernte landet auf dem Startbildschirm
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,OUT
S="{r0:500,rMin:200,shrink:4,step:50,head:2,dur:30,ping:120,pen:2,mode:'survive',taskR:0,imm:240,shOn:true,shT:10,evT:5,ddN:0,ddT:4,mtN:0,mtT:8,bon:true,hbOn:true,hbN:2,hbC:60,hbL:60,hbT:30,gw:20,gd:60,ot:5}"
def lobby(ev,me):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'lobby',rn:0,c:{lat:47.07,lng:15.44},s:%s,
        players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0725,lng:15.4385,ts:T},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0705,lng:15.4405,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.443,ts:T}},
        cols:{0:'u1',1:'u2',2:'u3'}}};
      uid='%s';const p=__T.games.K7QF.players['%s'];pos={lat:p.lat,lng:p.lng};lastFix=Date.now()})()"""%(S,me,me))
    ev("join('K7QF')")
with app(390,844) as (pg,ev,errs):
    lobby(ev,'u1');pg.wait_for_timeout(900)
    ev("tabGo('lt','players')");pg.wait_for_timeout(300)
    pg.click("button.lchip[aria-label^='Lena']");pg.wait_for_timeout(300)
    t=ev("document.getElementById('dlg').innerText");print(t.replace('\n',' | '));assert 'Aus der Lobby entfernen' in t and 'Zum Host machen' in t
    pg.screenshot(path=OUT+'/kick_menue.png')
    pg.click("#dlg [data-bi='1']");pg.wait_for_timeout(300)
    assert 'Spieler entfernen?' in ev("document.getElementById('dlg').textContent")
    pg.click("#dlo");pg.wait_for_timeout(600)
    assert ev("!G.players.u2") and ev("!(G.cols||{})[1]") and ev("!!G.players.u3"),ev("JSON.stringify(G.players)")
    # Abbrechen lässt alles, wie es ist
    pg.click("button.lchip[aria-label^='Max']");pg.wait_for_timeout(300);pg.click("#dlc");pg.wait_for_timeout(300)
    assert ev("!!G.players.u3") and not ev("!!document.getElementById('dlg')")
    assert not [e for e in errs if 'PE:' in e],errs
with app(390,844) as (pg,ev,errs):
    lobby(ev,'u2');pg.wait_for_timeout(900)
    ev("window.__toasts=[];const _t=toast;window.toast=m=>{__toasts.push(String(m));return _t(m)}")
    ev("delete __T.games.K7QF.players.u2;notify()");pg.wait_for_timeout(500)
    print(ev("__toasts"));assert any('entfernt' in x for x in ev("__toasts")) and ev("leaving")
    assert not [e for e in errs if 'PE:' in e],errs
print('ok')
