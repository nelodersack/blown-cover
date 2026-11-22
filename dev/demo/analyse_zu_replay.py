"""Analyse-Datei(en) → Replay-Datei(en), mit der App-eigenen Umwandlung (rvConv inkl. Funk aus Chat/Markern).
Aufruf: python3 dev/demo/analyse_zu_replay.py <ausgabeordner> analyse1.json [analyse2.json …]
Dateiname wie in der App: blowncover_replay_<CODE>_r<n>_<JJJJMMTT-HHMM>.json (Zeit = Spielstart, Europe/Vienna)."""
import os,sys,json,datetime
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
out=sys.argv[1];os.makedirs(out,exist_ok=True)
with app() as (pg,ev,errs):
    for f in sys.argv[2:]:
        o=json.load(open(f,encoding='utf-8'))
        r=pg.evaluate("o=>{const r=rvConv(o);r.generated=new Date().toISOString();return r}",o)
        st=datetime.datetime.fromtimestamp(r['game']['startAt']/1000,datetime.timezone(datetime.timedelta(hours=1)))
        name='blowncover_replay_%s_r%d_%s.json'%(r['code'],r['round'],st.strftime('%Y%m%d-%H%M'))
        json.dump(r,open(os.path.join(out,name),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
        F=r.get('funk') or {}
        print(name,'Spieler',len(r['players']),'Log',len(r['log']),'Chat',len(F.get('ch',[])),'Marker',len(F.get('mk',[])))
    print('errors:',errs)
