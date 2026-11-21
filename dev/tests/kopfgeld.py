# Test: Spielmodus „Kopfgeld“ (KONZEPT_Kopfgeld.md Teil B)
# 1) Lobby: 3 Teams, Teamfelder, Beitritt, Teamchef = frühester Beitritt (Krone, Name/Farbe nur er), Teamfarben für Hider gesperrt,
#    Start nur mit Hunter in jedem Team
# 2) Spiel: Hunter sehen nur ihr Team (Karte, Chat t<n>, Privat nur im Team, Marker-Pfad tmarks/<code>/<n>); Zuschauer lesen alle Teamkanäle
# 3) Endscreen: Team-Rangliste nach Fängen (Gleichstand → früherer letzter Fang), Hider „Du hast gewonnen/verloren“
# 4) Auslosen mit Teamzahl × Teamgröße; 5) Balancing mit effektiver Hunterzahl
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
NM=['Anna','Bert','Cora','Dani','Emil','Finn','Gabi','Hugo','Ida','Jan']
def players(running=False):
    pl={}
    for i,n in enumerate(NM):
        u='u%d'%i;p={'name':n,'role':'hunter' if i<6 else 'hider','state':'alive','j':i+1,'col':i%12}
        if i<6:p['tm']=i%3+1;p['tj']=100+i
        if running:p.update({'lat':47.07+i*3e-4,'lng':15.44+i*3e-4,'ts':0})
        pl[u]=p
    return pl
SET="""(()=>{const T=Date.now();__T['.info']={connected:true};const pl=%s;for(const k in pl)if(pl[k].lat)pl[k].ts=T;
  __T.games={%s:Object.assign({host:'u0',status:'%s',c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:3,head:0}),players:pl,teams:{2:{name:'Die Füchse'}}},%s)};
  notify();uid='%s';pos={lat:47.07,lng:15.44};lastFix=T;0})()"""
with app(width=412,height=915) as (pg,ev,errs):
    ev(SET%(json.dumps(players()),'KOPF','lobby','{}','u0'));ev("join('KOPF')");pg.wait_for_timeout(900)
    ev("ui.lt='players';panel(1)");pg.wait_for_timeout(300)
    t=ev("$('pb').innerText.replace(/\\n/g,' | ')");print('lobby:',t[:400])
    assert 'Agentur 1' in t and 'Die Füchse' in t and 'Agentur 3' in t
    print('Chefs:',[ev("tmChef(%d)"%n) for n in (1,2,3)]);assert [ev("tmChef(%d)"%n) for n in (1,2,3)]==['u0','u1','u2']
    print('Teamfarben:',ev("JSON.stringify(tmCols(G))"),'gesperrt für Hider:',ev("[...colBlk()]"))
    assert ev("[...colBlk()].sort().join()")=='0,1,2'
    # Hider u6 hat Farbe 6 (frei) – Hider u7 bekommt eine Teamfarbe zugeschoben → tmCheck wählt neu
    ev("__T.games.KOPF.players.u7.col=1;notify()");pg.wait_for_timeout(200);ev("uid='u7';G=__T.games.KOPF;tmCheck()");pg.wait_for_timeout(400);ev("uid='u0';panel(1)");pg.wait_for_timeout(200)
    c7=ev("__T.games.KOPF.players.u7.col");print('Hider mit Teamfarbe → neu:',c7);assert c7 not in (0,1,2)
    # nur der Chef sieht Name/Farbe-Knöpfe an seinem Team
    print('Knöpfe als Chef von Team 1:',ev("document.querySelectorAll('.ltm')[0].querySelectorAll('.lib').length"),'bei Team 2:',ev("document.querySelectorAll('.ltm')[1].querySelectorAll('.lib').length"))
    assert ev("document.querySelectorAll('.ltm')[0].querySelectorAll('.lib').length")==2 and ev("document.querySelectorAll('.ltm')[1].querySelectorAll('.lib').length")==0
    ev("tmPalTog(1)");pg.wait_for_timeout(200);shot(pg,'kopfgeld_lobby.png')
    ev("tmColPick(1,1)");pg.wait_for_timeout(200);print('fremde Teamfarbe:',ev("$('toast').innerText"));assert 'anderes Team' in ev("$('toast').innerText")
    ev("tmColPick(1,5)");pg.wait_for_timeout(300);print('neue Farbe Team 1:',ev("tmCols(G)[1]"));assert ev("tmCols(G)[1]")==5
    # Wechsel: u3 (Team 1) geht zu Team 3 → Chef von Team 3 bleibt u2
    ev("uid='u3';G=__T.games.KOPF;tmJoin(3)");pg.wait_for_timeout(300);ev("uid='u0'");print('Team 3:',[m[0] for m in ev("tmMem(3)")],'Chef',ev("tmChef(3)"))
    assert ev("tmChef(3)")=='u2' and 'u3' in [m[0] for m in ev("tmMem(3)")]
    # Start mit leerem Team scheitert
    ev("__T.games.KOPF.s.tN=4;notify()");pg.wait_for_timeout(300);ev("st()");pg.wait_for_timeout(600);print('Start mit leerem Team:',ev("$('toast').innerText"))
    assert 'Agentur 4' in ev("$('toast').innerText")
    # Balancing: 3 Teams à 2 gegen 4 Hider → H_eff = 2 · 2 = 4
    b=ev("(()=>{const s=Object.assign({},DEF,PRE[30],{dur:30,mode:'bounty',tN:3});const a=balCalc(s,6,4,2).o,b=balCalc(Object.assign({},s,{mode:'survive'}),4,4,2).o;return [a.r0,a.ping,b.r0,b.ping]})()")
    print('Balancing Kopfgeld 3×2/4 = Überleben 4/4:',b);assert b[0]==b[2] and b[1]==b[3]
    e1=errs[:]

# 2) Spiel: Sichtbarkeit, Chat, Marker
with app(width=412,height=915) as (pg,ev,errs):
    ev(SET%(json.dumps(players(True)),'KOPG','running',"{startAt:Date.now()-60000}",'u0'));ev("join('KOPG')");pg.wait_for_timeout(1200)
    mates=ev("document.querySelectorAll('.mkw.mate').length");print('Mitspieler auf der Karte (Team 1 = u0,u3):',mates);assert mates==1
    print('Kanäle:',ev("chChans()"),'Privat mit:',ev("mates()"),'Pfad:',ev("chPath('t1')"),ev("chPath('dm:u3')"),'Marker:',ev("mkB()"))
    assert ev("chChans()")==['t1'] and ev("mates()")==['u3'] and ev("chPath('dm:u3')").startswith('chats/KOPG/dm/t1/') and ev("mkB()")=='tmarks/KOPG/1'
    assert ev("chCanWrite('t1')") and not ev("chCanWrite('t2')") and not ev("chCanWrite('hunter')")
    shot(pg,'kopfgeld_spiel.png')
    # Zuschauer
    ev("__T.games.KOPG.players.sx={name:'Zara',role:'spec',state:'spec',j:99};uid='sx';notify()");pg.wait_for_timeout(300)
    print('Zuschauer liest:',ev("chChans()"));assert ev("chChans()")==['out','hider','t1','t2','t3']
    # 3) Ende: Team 2 fängt u6 und u7 (zuletzt nach 5 Min), Team 1 fängt u8 → Team 2 vorn; u9 frei
    ev("""(()=>{const g=__T.games.KOPG,T=g.startAt,ps=g.players;
      g.catches={u6:{hunter:'u1',status:'done',t:T+2*60000},u7:{hunter:'u4',status:'done',t:T+5*60000},u8:{hunter:'u0',status:'done',t:T+3*60000}};
      ['u6','u7','u8'].forEach(k=>{ps[k].state='caught';ps[k].sT=g.catches[k].t});g.status='over';g.winner='hider';uid='u0';notify()})()""");pg.wait_for_timeout(600)
    r=ev("$('resb').innerText.replace(/\\n/g,' | ')");print('Endscreen Hunter u0:',r[:300])
    assert r.startswith('Die Füchse gewinnt') and 'Ihr seid Zweiter' in r
    shot(pg,'kopfgeld_ende.png')
    ev("uid='u9';resSync(G)");pg.wait_for_timeout(200);r=ev("$('resb').innerText");print('Hider u9:',r[:40]);assert r.startswith('Du hast gewonnen')
    ev("uid='u6';resSync(G)");pg.wait_for_timeout(200);r=ev("$('resb').innerText.replace(/\\n/g,' | ')");print('Hider u6:',r[:80]);assert r.startswith('Du hast verloren') and 'Die Füchse' in r
    # Gleichstand: Team 1 fängt auch u9 nach 4 Min → 2:2, Team 1 letzter Fang 4 Min < Team 2 5 Min → Team 1 gewinnt
    ev("""(()=>{const g=__T.games.KOPG;g.catches.u9={hunter:'u3',status:'done',t:g.startAt+4*60000};g.players.u9.state='caught';uid='u0';notify()})()""");pg.wait_for_timeout(400)
    rk=ev("tmRank(G).map(t=>t.name+':'+t.f)");print('Gleichstand:',rk);assert rk[0]=='Agentur 1:2'
    e2=errs[:]

# 4) Auslosen: 2 Teams à 2 aus 7 Spielern
with app(width=412,height=915) as (pg,ev,errs):
    pl={'u%d'%i:{'name':NM[i],'role':'hider','state':'alive','j':i+1,'col':i} for i in range(7)}
    ev(SET%(json.dumps(pl),'KOPR','lobby','{}','u0'));ev("__T.games.KOPR.s=Object.assign(__T.games.KOPR.s,{tN:2,tS:2,rnd:true});__T.games.KOPR.players.u0.lat=47.07;notify()")
    ev("join('KOPR')");pg.wait_for_timeout(800);ev("chkGps=async()=>[];mkPts=async(c,r,n)=>({pts:Array.from({length:n},(_,i)=>({lat:47.07+i*1e-4,lng:15.44}))})")
    ev("st()");pg.wait_for_timeout(1500)
    ps=ev("Object.values(__T.games.KOPR.players).map(p=>p.role+(p.tm||''))");print('ausgelost:',ps,ev("__T.games.KOPR.status"))
    assert ev("__T.games.KOPR.status")=='running' and sorted(ps).count('hunter1')==2 and sorted(ps).count('hunter2')==2 and ps.count('hider')==3
    e3=errs[:]
    print('errors:',e1+e2+e3+errs[:4] if False else (e1+e2+e3)[:8])
