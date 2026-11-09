# Test: Panel wird ohne Zustandsänderung nicht neu aufgebaut (Neuaufbau ließ am iPhone die Seite beim Scrollen springen); Countdowns laufen trotzdem
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ux_feinschliff.py')).read().split('# 1 Lobby')[0])
WATCH="window.__n=0;new MutationObserver(()=>__n++).observe($('pb'),{childList:true})"
for me,st,nm in [('u1','lobby','Hunter Lobby'),('u1','running','Hunter Spiel'),('u2','running','Hider Spiel')]:
    with app(390,844) as (pg,ev,errs):
        game(ev,me,st);go(ev,pg);pg.wait_for_timeout(1500);ev(WATCH);pg.wait_for_timeout(11000)
        n=ev("__n");print(nm,'Neuaufbauten in 11 s:',n);assert n==0
        assert not [e for e in errs if 'PE:' in e]
# Hunter mit Bonus im Cooldown: Text zählt, Panel bleibt
with app(390,844) as (pg,ev,errs):
    game(ev,'u1');ev("__T.games.K7QF.hb={u1:{x1:{k:'live',av:Date.now()+20000}}}");go(ev,pg);pg.wait_for_timeout(1500);ev(WATCH)
    a=ev("(document.querySelector('#pb [data-cd]')||{}).textContent");pg.wait_for_timeout(3200);b=ev("(document.querySelector('#pb [data-cd]')||{}).textContent")
    print('Cooldown',a,'->',b,'Neuaufbauten',ev("__n"));assert a and b and a!=b and ev("__n")==0
    print('errors:',[e for e in errs if 'PE:' in e]);assert not [e for e in errs if 'PE:' in e]
