# Test: Lobby-Chat für alle (Kanal all, keine Privatnachrichten, Rolle neben dem Namen, bei Auslosen ohne Rolle);
# ab Spielstart wieder Team-Chat
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app() as (pg,ev,errs):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={LOBX:{host:'u1',status:'lobby',c:{lat:47.07,lng:15.44},s:{r0:500,rMin:200,shrink:5,step:50,head:0,dur:60,ping:600,mode:'survive'},
        players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0},u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1},u9:{name:'Max',role:'hider',state:'alive',j:3,col:2}},cols:{0:'u1',1:'u2',2:'u9'}}};
      __T.chats={LOBX:{all:{a:{u:'u1',n:'Anna',t:T,x:'Wer jagt?',r:'hunter'}}}};
      uid='u9';pos={lat:47.07,lng:15.44};lastFix=Date.now()})()""")
    ev("join('LOBX')");pg.wait_for_timeout(1200)
    ev("chToggle(true)");pg.wait_for_timeout(300)
    tabs=ev("$('cht').innerText");print('reiter:',tabs,'| kanal:',ev("chCur"))
    assert ev("chCur")=='all' and 'Privat' not in tabs and 'Alle' in tabs
    msg=ev("$('chm').innerText.replace(/\\n/g,' | ')");print('nachrichten:',msg)
    assert 'Anna · Hunter' in msg
    ev("$('chi').value='Ich bin dabei';chSend()");pg.wait_for_timeout(400)
    print('gespeichert:',ev("JSON.stringify(Object.values(__T.chats.LOBX.all).map(c=>c.x+'/'+c.r))"))
    assert 'Ich bin dabei/hider' in ev("JSON.stringify(Object.values(__T.chats.LOBX.all).map(c=>c.x+'/'+c.r))")
    shot(pg,'chat_lobby.png')
    # Auslosen an → keine Rollen
    ev("__T.games.LOBX.s.rnd=true;notify()");pg.wait_for_timeout(500)
    msg=ev("$('chm').innerText.replace(/\\n/g,' | ')");print('auslosen:',msg)
    assert '· Hunter' not in msg and '· Hider' not in msg and 'Wer jagt?' in msg
    # Spielstart → Team-Chat mit Privat
    ev("__T.games.LOBX.s.rnd=false;__T.games.LOBX.status='running';__T.games.LOBX.startAt=Date.now()-60000;notify()");pg.wait_for_timeout(600)
    print('im spiel:',ev("chCur"),'|',ev("$('cht').innerText"))
    assert ev("chCur")=='hider' and 'Team' in ev("$('cht').innerText") and 'Privat' in ev("$('cht').innerText")
    print('errors:',errs[:8])
