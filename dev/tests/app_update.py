# Test: App-Update (GitHub Releases). App mit älterer Version → Dialog beim Öffnen + Knopf mit orangem Punkt auf dem
# Startbildschirm; aktuelle App → nichts; Android-Browser → dezenter Link; Lobby → kein Knopf
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
FETCH="""(()=>{const f=window.fetch;window.__rel=0;window.fetch=(u,o)=>{if(String(u).includes('api.github.com')){window.__rel++;
  return Promise.resolve({ok:true,json:()=>Promise.resolve({tag_name:'v0.3.4',assets:[{name:'BlownCover.apk'}]})})}return f(u,o)}})();"""
NB=lambda v:"window.BlownNative={info:()=>JSON.stringify({app:1,ver:'%s'}),ready:()=>true,log:()=>{},keepAwake:()=>{},stopTracking:()=>{},lastPos:()=>'',notify:()=>{},saveFile:()=>{}};"%v
TXT="document.getElementById('pb').innerText.replace(/\\n/g,' | ')"

# 1) App 0.3.3, neueste 0.3.4 → Dialog + Knopf
with app(init=FETCH+NB('0.3.3')) as (pg,ev,errs):
    ev("__T['.info']={connected:true};notify()");pg.wait_for_timeout(1500)
    print('dlg:',ev("(document.getElementById('dlg')||{}).innerText"))
    assert 'Update verfügbar' in ev("(document.getElementById('dlg')||{}).innerText||''")
    shot(pg,'app_update_dialog.png')
    ev("document.querySelector('#dlg button:not(.pri)')&&[...document.querySelectorAll('#dlg button')].find(b=>/Später/.test(b.innerText)).click()");pg.wait_for_timeout(400)
    print('start:',ev(TXT))
    assert 'App-Update laden' in ev(TXT) and ev("!!document.querySelector('.upd i')")
    shot(pg,'app_update_start.png')
    print('cache:',ev("LS.updC"))
    # Lobby: kein Knopf
    ev("""(()=>{const T=Date.now();__T.games={LOBX:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:600,mode:'survive'},players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0}}}};uid='u9';pos={lat:47.07,lng:15.44};lastFix=Date.now()})()""")
    ev("join('LOBX')");pg.wait_for_timeout(1200)
    print('lobby upd?',ev("!!document.querySelector('.upd')"))
    assert not ev("!!document.querySelector('.upd')")
    print('errors:',errs[:8]);e1=errs[:]

# 2) App aktuell → kein Dialog, kein Knopf; zweites Öffnen nutzt Cache
with app(init=FETCH+NB('0.3.4')) as (pg,ev,errs):
    pg.wait_for_timeout(1200)
    print('aktuell dlg?',ev("!!document.getElementById('dlg')"),'knopf?',ev("!!document.querySelector('.upd')"),'abfragen',ev("__rel"))
    assert not ev("!!document.getElementById('dlg')") and not ev("!!document.querySelector('.upd')")
    print('errors:',errs[:8]);e2=errs[:]

# 3) Android-Browser ohne App → dezenter Link, kein Dialog
with app(init=FETCH+"Object.defineProperty(navigator,'userAgent',{get:()=>'Mozilla/5.0 (Linux; Android 14; SM-S901B) Chrome/130 Mobile'});") as (pg,ev,errs):
    pg.wait_for_timeout(1200)
    print('browser:',ev(TXT)[-80:],'dlg?',ev("!!document.getElementById('dlg')"))
    assert 'als Android-App laden' in ev(TXT) and not ev("!!document.getElementById('dlg')")
    shot(pg,'app_update_browser.png')
    print('errors:',errs[:8]+e1+e2)
