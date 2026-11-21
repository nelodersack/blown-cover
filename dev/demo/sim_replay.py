"""Simulierte Demo-Replays (Untertauchen und Kopfgeld) zum Anschauen von Replay, Blickwinkel, Funk und Sprechblasen.

Aufruf:  python3 dev/demo/sim_replay.py [ausgabeordner]   (Standard: dev/out)
Erzeugt blowncover_replay_DEMO-UNTERTAUCHEN.json und blowncover_replay_DEMO-KOPFGELD.json.

Die Runde wird im Browser (Playwright, App-Code für Einstellungen/Zonen) Schritt für Schritt simuliert:
- Hider verstecken sich, wechseln ab und zu das Versteck und fliehen, wenn ein Hunter nahe kommt.
- Hunter laufen zur letzten Ping-Position eines Hiders, suchen dort und jagen ihn, sobald er in Sichtweite ist.
- Fang bei < 6 m. Extra-Ping, Live-Standort, Safehouse, Chat (Team + privat) und Marker entstehen aus den Ereignissen.
Wege laufen frei über die Karte (keine Straßen).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app, OUT

SIM = r"""
(cfg)=>{
  let sd=cfg.seed;const rnd=()=>{sd|=0;sd=sd+0x6D2B79F5|0;let t=Math.imul(sd^sd>>>15,1|sd);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
  const pick=a=>a[Math.floor(rnd()*a.length)];
  const C={lat:47.0738,lng:15.4462},MY=111195,MX=111195*Math.cos(C.lat*Math.PI/180);
  const ll=p=>[+(C.lat+p.y/MY).toFixed(6),+(C.lng+p.x/MX).toFixed(6)];
  const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const s=Object.assign({},DEF,preOf(30),{mode:cfg.mode,rp:true,dur:30,hbOn:true,hbN:2,hbC:60,hbL:60,shOn:true,shT:4,ddN:0,mtN:0,hk:false,bon:true});
  if(cfg.mode==='bounty')s.tN=cfg.teams.length;if(cfg.r0){s.r0=cfg.r0;s.rMin=cfg.rMin}
  const T0=Date.UTC(2026,10,22,14,0,0),R0=T0+s.head*6e4,END=R0+s.dur*6e4,DT=5000;
  const rad=t=>RadS(s,Math.max(0,t-R0));
  // Spieler
  const pl=[],P={};let j=0;
  cfg.hunters.forEach(([n,tm])=>{const id='p'+(++j);const o={id,name:n,role:'hunter',col:tm?cfg.teams[tm-1].col:j-1,j,tm:tm||null,tmn:tm?cfg.teams[tm-1].name:null,state:'alive'};pl.push(o);
    const a=rnd()*2*Math.PI;P[id]={o,pos:{x:Math.cos(a)*40,y:Math.sin(a)*40},tgt:null,know:{},seen:null,last:0}});
  cfg.hiders.forEach((n,i)=>{const id='p'+(++j);const o={id,name:n,role:'hider',col:(cfg.hcol0+i)%12,j,state:'alive'};pl.push(o);
    P[id]={o,pos:{x:(rnd()-.5)*40,y:(rnd()-.5)*40},hide:null,mv:0}});
  const H=pl.filter(p=>p.role==='hunter').map(p=>p.id),X=pl.filter(p=>p.role==='hider').map(p=>p.id);
  const side=id=>{const o=P[id].o;return o.role==='hunter'?(o.tm?'t'+o.tm:'hunter'):'hider'};
  const tr={},log=[],ch=[],mk=[];pl.forEach(p=>tr[p.id]=[]);
  const say=(t,u,chan,x)=>ch.push([Math.round(t),u,chan,x]);
  const dm=(t,u,v,x)=>{const a=[u,v].sort();say(t,u,'d:'+side(u)+':'+a[0]+'_'+a[1],x)};
  const alive=id=>P[id].o.state==='alive';
  const randIn=(r)=>{const a=rnd()*2*Math.PI,d=Math.sqrt(rnd())*r;return{x:Math.cos(a)*d,y:Math.sin(a)*d}};
  const step=(p,to,v)=>{const d=dist(p,to);if(d<=v*DT/1000)return{x:to.x,y:to.y};const f=v*DT/1000/d;return{x:p.x+(to.x-p.x)*f,y:p.y+(to.y-p.y)*f}};
  const inZone=(p,t,m)=>{const r=rad(t)*(m||.92),d=Math.hypot(p.x,p.y);return d<=r?p:{x:p.x/d*r,y:p.y/d*r}};
  // Safehouse
  const shLoc=randIn(rad(R0)*.6),shT=R0+s.shT*6e4,shL=ll(shLoc);let shN=0;
  log.push([shT,'tasks/sh/t0',shT],[shT,'tasks/sh/loc/lat',shL[0]],[shT,'tasks/sh/loc/lng',shL[1]]);
  let mkN=0;const mark=(t,k,u,p,extra)=>{const id='m'+(++mkN),q=ll(p);mk.push([Math.round(t),'+',id,k,q[0],q[1],extra&&extra.r||null,extra&&extra.x||null,u,extra&&extra.h||null]);return id};
  const unmark=(t,id)=>mk.push([Math.round(t),'-',id]);
  const pingEvery=s.ping*1000;let nextPing=R0+pingEvery;
  const xpAt=R0+cfg.xpMin*6e4,liveAt=R0+cfg.liveMin*6e4;let xpDone=0,liveDone=0,liveTo=null,liveUntil=0,satDone=0;
  const lastSay={};const rl=(k,t,ms)=>{if(lastSay[k]&&t-lastSay[k]<ms)return false;lastSay[k]=t;return true};
  const HT=cfg.chat;
  for(let t=T0;t<=END;t+=DT){
    // Hider
    X.forEach(id=>{const q=P[id];if(!alive(id))return;
      let thr=null,td=1e9;H.forEach(h=>{const d=dist(P[h].pos,q.pos);if(d<td){td=d;thr=h}});
      if(t<R0){if(!q.hide)q.hide=randIn(rad(R0)*.8);q.pos=step(q.pos,q.hide,2.2)}
      else if(td<85){const away={x:q.pos.x+(q.pos.x-P[thr].pos.x),y:q.pos.y+(q.pos.y-P[thr].pos.y)};q.pos=inZone(step(q.pos,away,2.6),t,.97);q.hide=null;
        if(rl('flee'+id,t,90000))say(t,id,'hider',pick(HT.flee));}
      else{if(!q.hide||rnd()<DT/(7*6e4)){q.hide=inZone(randIn(rad(t)*.85),t)}
        if(q.sh&&t<q.sh.until)q.hide=shLoc;
        q.pos=inZone(step(q.pos,q.hide,dist(q.pos,q.hide)>30?1.4:.15),t)}
      // Safehouse: die ersten zwei
      if(t>=shT&&shN<2&&!q.shv&&dist(q.pos,shLoc)<400&&rnd()<.02){q.sh={until:t+6e4*4};q.shv=1}
      if(q.sh&&!q.shIn&&dist(q.pos,shLoc)<20&&shN<2){q.shIn=1;shN++;log.push([t,'tasks/sh/in/'+id+'/t',t]);log.push([t,'players/'+id+'/immUntil',t+s.imm*1000]);say(t,id,'hider',pick(HT.safe))}
    });
    // Ping
    if(t>=nextPing){const pt=nextPing;nextPing+=pingEvery;
      X.forEach(id=>{if(alive(id))H.forEach(h=>{P[h].know[id]={p:{...P[id].pos},t:pt}})});
      H.forEach(h=>{const q=P[h];if(!alive(h))return;let best=null,bd=1e9;X.forEach(id=>{if(!alive(id))return;const k=q.know[id];const d=dist(q.pos,k.p)+rnd()*120+(cfg.mode==='bounty'&&H.some(o=>o!==h&&side(o)!==side(h)&&P[o].tgt===id)?400:0);if(d<bd){bd=d;best=id}});
        if(best){q.tgt=best;if(rnd()<.35&&rl('pm'+h,t,4*6e4)){const m=mark(pt+8000,'excl',h,q.know[best].p,{h:best});q.mk=m}
          if(rnd()<.45&&rl('ps'+side(h),t,2*6e4))say(pt+15000+rnd()*20000,h,side(h),pick(HT.ping).replace('%',P[best].o.name))}});
      H.forEach(h=>{if(P[h].mk&&rnd()<.6){unmark(pt+pingEvery-1000,P[h].mk);P[h].mk=null}})}
    // Extra-Ping (ein Hunter) und Live-Standort (ein anderer)
    if(!xpDone&&t>=xpAt){xpDone=1;const h=H[cfg.xpH];log.push([t,'hb/'+h+'/b1/k','xp'],[t,'hb/'+h+'/b1/u',t]);
      X.forEach(id=>{if(alive(id))H.filter(x=>side(x)===side(h)).forEach(x=>P[x].know[id]={p:{...P[id].pos},t})});say(t+5000,h,side(h),HT.xp)}
    if(!liveDone&&t>=liveAt){liveDone=1;const h=H[cfg.liveH];let best=null,bd=1e9;X.forEach(id=>{if(!alive(id))return;const d=dist(P[h].pos,P[id].pos);if(d<bd){bd=d;best=id}});
      if(best){liveTo=best;liveUntil=t+s.hbL*1000;log.push([t,'hb/'+h+'/b2/k','live'],[t,'hb/'+h+'/b2/u',t],[t,'live/'+best+'/'+h,liveUntil]);P[h].tgt=best;say(t+4000,h,side(h),HT.live.replace('%',P[best].o.name))}}
    // Hunter
    H.forEach(h=>{const q=P[h];if(t<R0)return;let goal=null,v=1.8;
      if(liveTo&&t<liveUntil&&alive(liveTo)&&H[cfg.liveH]===h){goal=P[liveTo].pos;v=2.6}
      let vis=null,vd=1e9;X.forEach(id=>{if(!alive(id))return;const d=dist(q.pos,P[id].pos);if(d<75&&d<vd&&!((P[id].sh||{}).until>t&&dist(P[id].pos,shLoc)<25)){vd=d;vis=id}});
      if(vis&&q.rest>t)vis=null;if(vis){if(!q.cs||q.tgt!==vis)q.cs=t;if(t-q.cs>70000){q.rest=t+60000;q.cs=0;q.tgt=null;if(rl('lost'+h,t,3*6e4))say(t,h,side(h),pick(HT.lost).replace('%',P[vis].o.name));vis=null}}
      if(vis){goal=P[vis].pos;v=3.3;if(q.tgt!==vis){q.tgt=vis;if(rl('see'+h,t,3*6e4))say(t,h,side(h),pick(HT.see).replace('%',P[vis].o.name))}}
      if(!goal&&q.tgt&&alive(q.tgt)&&q.know[q.tgt]){const k=q.know[q.tgt].p;goal=dist(q.pos,k)>25?k:(q.srch&&dist(q.pos,q.srch)>8?q.srch:(q.srch={x:k.x+(rnd()-.5)*140,y:k.y+(rnd()-.5)*140}))}
      if(!goal){if(!q.wan||dist(q.pos,q.wan)<10)q.wan=randIn(rad(t)*.8);goal=q.wan}
      q.pos=inZone(step(q.pos,goal,v),t,.99);
      if(vis&&vd<6&&alive(vis)&&!P[vis].dodged&&rnd()<.35){P[vis].dodged=1;const a=rnd()*2*Math.PI;P[vis].pos=inZone({x:P[vis].pos.x+Math.cos(a)*45,y:P[vis].pos.y+Math.sin(a)*45},t,.97);q.rest=t+45000;q.tgt=null;say(t+4000,vis,'hider',pick(HT.dodge));if(rl('lost'+h,t,6e4))say(t+6000,h,side(h),pick(HT.lost).replace('%',P[vis].o.name))}
      else if(vis&&vd<6&&alive(vis)){const xo=P[vis].o;xo.state='caught';log.push([t,'catches/'+vis+'/hunter',h],[t,'catches/'+vis+'/status','done'],[t,'catches/'+vis+'/t',t],[t,'players/'+vis+'/state','caught'],[t,'players/'+vis+'/sT',t]);
        say(t+3000,h,side(h),pick(HT.catch).replace('%',xo.name));say(t+9000,vis,'hider',pick(HT.caught));q.tgt=null;q.srch=null}});
    pl.forEach(p=>{const q=P[p.id];if(p.state!=='alive'&&p.role==='hider'&&tr[p.id].length&&tr[p.id][tr[p.id].length-1][0]>=+(log.find(x=>x[1]==='players/'+p.id+'/sT')||[0])[0]+6e4)return;
      const g=ll(q.pos),jit=()=>(rnd()-.5)*2/MY*3;tr[p.id].push([t,+(g[0]+jit()).toFixed(6),+(g[1]+jit()).toFixed(6),Math.round(5+rnd()*8)])});
    if(X.every(id=>!alive(id)))break}
  // feste Gespräche aus der Konfiguration (Zeit in Minuten nach Headstart-Ende)
  (cfg.talk||[]).forEach(([m,u,chan,x,to])=>{const t=R0+m*6e4,uid=pl.find(p=>p.name===u).id;if(to)dm(t,uid,pl.find(p=>p.name===to).id,x);else say(t,uid,chan==='side'?side(uid):chan,x)});
  const free=X.filter(alive),endT=free.length?END:Math.max(...log.filter(x=>/\/sT$/.test(x[1])).map(x=>x[0]));
  const ch2=ch.filter(x=>x[0]<=endT).sort((a,b)=>a[0]-b[0]),mk2=mk.filter(x=>x[0]<=endT);
  const teams=cfg.mode==='bounty'?Object.fromEntries(cfg.teams.map((x,i)=>[i+1,{name:x.name,col:x.col}])):null;
  return{format:'blown-cover-replay',v:2,code:cfg.code,round:0,generated:new Date(T0).toISOString(),
    game:{s,c:C,teams,startAt:T0,R0,end:endT,winner:free.length?'hider':'hunter'},players:pl,tracks:tr,log:log.sort((a,b)=>a[0]-b[0]),funk:{ch:ch2,mk:mk2}}}
"""

CHAT = {
  'flee': ['Hunter direkt bei mir, ich renne!', 'Mist, die haben mich gesehen', 'Ich muss weg, jemand kommt', 'Zu nah, ich lauf Richtung Fluss'],
  'safe': ['Bin im Safehouse', 'Safehouse erreicht, kurz durchatmen'],
  'ping': ['Ping: % ist im Süden', 'Ich nehme %', '% steht seit zwei Pings am selben Fleck', 'Wer geht auf %?'],
  'see': ['Ich sehe %!', '% direkt vor mir', 'Hab % im Blick, komm rüber'],
  'catch': ['% gefangen!', 'Hab %', '% erwischt'],
  'dodge': ['Puh, das war knapp!', 'Haarscharf entkommen', 'Der hatte mich fast'],
  'lost': ['% ist mir entwischt', 'Kann nicht mehr, % ist weg', 'Verloren, % ist zu schnell'],
  'caught': ['Ich bin raus, viel Glück', 'Erwischt… passt auf euch auf', 'Die waren zu schnell'],
  'xp': 'Extra-Ping eingesetzt, schaut auf die Karte', 'live': 'Live-Standort auf %, ich hänge mich dran',
}

UNTER = dict(code='DEMOU', seed=9, mode='survive', hcol0=2, chat=CHAT, xpMin=11, xpH=0, liveMin=17, liveH=1,
  hunters=[('Manuel', 0), ('Sophie', 0)], hiders=['Lena', 'Jakob', 'Mira', 'Felix', 'Nora'], teams=[],
  talk=[(1, 'Lena', 'hider', 'Ich gehe Richtung Stadtpark-Brunnen'), (1.5, 'Felix', 'hider', 'Ich bleib im Westen'),
        (3, 'Manuel', 'side', 'Ich nehme den Norden, du den Süden?'), (3.3, 'Sophie', 'side', 'Passt'),
        (6, 'Mira', None, 'Treffen wir uns später am Safehouse?', 'Nora'), (6.4, 'Nora', None, 'Ja, aber erst nach dem nächsten Ping', 'Mira'),
        (9, 'Sophie', None, 'Ich glaube Jakob versteckt sich im Gebüsch', 'Manuel'), (9.3, 'Manuel', None, 'Check ich gleich', 'Sophie'),
        (14, 'Jakob', 'hider', 'Wie viele Hunter sind im Osten?'), (21, 'Lena', None, 'Bist du noch frei?', 'Felix'), (21.4, 'Felix', None, 'Ja, liege flach', 'Lena')])

KOPF = dict(code='DEMOK', seed=9, r0=950, rMin=400, mode='bounty', hcol0=6, chat=CHAT, xpMin=10, xpH=2, liveMin=16, liveH=0,
  teams=[{'name': 'Die Füchse', 'col': 10}, {'name': 'Schattenkartell', 'col': 11}, {'name': 'Agentur Nord', 'col': 0}],
  hunters=[('Manuel', 1), ('Sophie', 1), ('Tobias', 2), ('Anna', 2), ('Lukas', 3), ('Clara', 3)],
  hiders=['Lena', 'Jakob', 'Mira', 'Felix', 'Nora'],
  talk=[(1, 'Manuel', 'side', 'Füchse, wir gehen gemeinsam über die Brücke'), (1.2, 'Tobias', 'side', 'Wir holen uns den ersten Fang'),
        (1.5, 'Lukas', 'side', 'Nord bleibt im Norden, klar?'), (2, 'Lena', 'hider', 'Drei Teams, passt auf euch auf!'),
        (5, 'Sophie', None, 'Das Kartell ist hinter uns', 'Manuel'), (5.4, 'Manuel', None, 'Egal, wir sind schneller', 'Sophie'),
        (8, 'Anna', None, 'Lass die Füchse laufen, wir warten am Ausgang', 'Tobias'), (12, 'Clara', 'side', 'Hab zwei Teams am Teich gesehen'),
        (15, 'Mira', None, 'Die Teams laufen sich gegenseitig über den Weg', 'Nora'), (22, 'Felix', 'hider', 'Noch 8 Minuten, durchhalten')])

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(out, exist_ok=True)
    with app(width=412, height=915) as (pg, ev, errs):
        for name, cfg in (('UNTERTAUCHEN', UNTER), ('KOPFGELD', KOPF)):
            f = pg.evaluate('(' + SIM + ')', cfg)
            fn = os.path.join(out, 'blowncover_replay_DEMO-%s.json' % name)
            json.dump(f, open(fn, 'w'), ensure_ascii=False, separators=(',', ':'))
            ev("G=null;code=null")
            pg.evaluate('f=>rvLoad(f)', f); pg.wait_for_timeout(600)
            st = ev("({ev:RV.ev.length,catch:RV.ev.filter(e=>e.k==='catch').length,knapp:RV.ev.filter(e=>e.k==='knapp').length,duel:RV.ev.filter(e=>e.k==='duel').length,h2h:(RV.st.h2h||[]).length,sn:(RV.st.snatch||[]).length,ch:RV.ch.length,dm:RV.ch.filter(x=>x.to).length,mk:RV.mki.length,win:rvWinT(RV.f.game),min:Math.round((RV.T1-RV.f.game.R0)/6e4)})")
            print(name, fn, st)
            ev("rvClose()")
        print('errors:', errs[:5])
