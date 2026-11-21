# Test: Farbregel für alle Modi (KONZEPT_Kopfgeld.md Teil A) – Farben schichtweise: erst jede Farbe einmal, dann jede zweimal, dann
# dreimal … Manuelle Wahl nur aus den Farben mit der niedrigsten Belegung; wer geht, macht seine Farbe frei; keine Obergrenze (26 Spieler);
# automatische Wahl bevorzugt anderen Anfangsbuchstaben; Zuschauer belegen keine Farbe.
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
N=['Anna','Bert','Cora','Dani','Emil','Finn','Gabi','Hugo','Ida','Jan','Kim','Lea','Max','Nina','Otto','Pia','Quentin','Rita','Sven','Tara','Udo','Vera','Wim','Xaver','Yara','Zoe']
CNT="(()=>{const n=Array(12).fill(0);Object.entries(P()).forEach(([k,p])=>{if(!p.lf&&isPl(p)&&Number.isInteger(p.col))n[p.col%12]++});return n})()"
with app(width=412,height=915) as (pg,ev,errs):
    pl={'u%d'%i:{'name':N[i],'role':'hider','state':'alive','j':i+1} for i in range(26)}
    pl['sx']={'name':'Zuschauer','role':'spec','state':'spec','j':99,'col':0}
    ev("""(()=>{__T['.info']={connected:true};__T.games={FARB:{host:'u0',status:'lobby',c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30)),players:%s}};
      notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=Date.now();0})()"""%json.dumps(pl))
    ev("join('FARB')");pg.wait_for_timeout(800)
    def auto(i):ev("(async()=>{uid='u%d';G=__T.games.FARB;await autoCol();notify()})()"%i);pg.wait_for_timeout(40)
    for i in range(13):auto(i)
    n=ev(CNT);print('13 Spieler:',n);assert sorted(n)==[1]*11+[2], n
    # 14. Spieler will eine schon doppelte Farbe → gesperrt; eine einfach belegte → erlaubt
    ev("uid='u13';G=__T.games.FARB");d=ev(CNT).index(2);e=ev(CNT).index(1)
    ev("palPick(%d)"%d);pg.wait_for_timeout(200);print('doppelte gewählt:',ev("P().u13.col"),ev("$('toast').innerText"))
    assert ev("P().u13.col")is None and 'gleich oft' in ev("$('toast').innerText")
    ev("palPick(%d)"%e);pg.wait_for_timeout(200);assert ev("P().u13.col")==e
    for i in range(14,24):auto(i)
    n=ev(CNT);print('24 Spieler:',n);assert n==[2]*12, n
    auto(24);auto(25);n=ev(CNT);print('26 Spieler:',n);assert sorted(n)==[2]*10+[3,3], n
    # Spieler mit dreifacher Farbe geht → Farbe wieder frei; Zuschauer zählt nicht
    k=ev("Object.keys(P()).find(k=>k==='u24')");c=ev("P().u24.col");ev("__T.games.FARB.players.u24.lf=true;notify()");pg.wait_for_timeout(200)
    n=ev(CNT);print('nach Verlassen:',n);assert n[c]==2
    # anderer Anfangsbuchstabe bevorzugt: Ida (I) kommt dazu, alle Farben gleich → nimmt keine Farbe mit einem I
    ev("uid='u0';ui.pal=1;panel(1)");pg.wait_for_timeout(300);shot(pg,'farben_schicht.png')
    print('Farbwahl:',ev("[...document.querySelectorAll('.pal .g span')].map(s=>s.innerText).join(',')"))
    print('errors:',errs[:8])
