# Test: halbe Karte nach dem Neuladen (22.11.). MapLibre übergeht den ersten ResizeObserver-Rückruf; ändert Leaflet die Größe
# im ersten Bild nach dem Anlegen der Vektorkarte, blieb der Canvas auf der alten Breite. vtFix zieht die Canvas-Größe nach.
# Läuft mit echtem MapLibre (vendor/) und einem Ersatz-Stil (nur Hintergrund), ohne Netz.
import os,sys,json
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STUB=open(os.path.join(ROOT,'dev','memdb.js'),encoding='utf-8').read()
STYLE=json.dumps({"version":8,"sources":{},"layers":[{"id":"background","type":"background","paint":{"background-color":"#ccc"}}]})
errs=[]
SZ="(()=>{const gl=vt&&vt.getMaplibreMap();return gl?[parseFloat(vt._container.style.width),gl.getCanvas().clientWidth,parseFloat(vt._container.style.height),gl.getCanvas().clientHeight]:null})()"
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':800}).new_page()
    pg.on('pageerror',lambda e:errs.append('PE:'+str(e)))
    def route(r):
        u=r.request.url
        if 'vendor/firebase-' in u: return r.fulfill(body=STUB if 'app-compat' in u else '',content_type='application/javascript')
        if 'openfreemap' in u: return r.fulfill(body=STYLE,content_type='application/json')
        if u.startswith('file:'): return r.continue_()
        return r.abort()
    pg.route('**/*',route)
    pg.goto('file://'+os.path.join(ROOT,'index.html')+'#test');pg.wait_for_timeout(1500)
    a=pg.evaluate(SZ);print('normal (Container/Canvas):',a);assert a and abs(a[0]-a[1])<=1
    # Größenwechsel im selben Bild wie das Anlegen der Vektorkarte (so entstand die halbe Karte)
    pg.evaluate("vt.remove();const s=$('map').style;s.right='auto';s.width='180px';map.invalidateSize();vt=L.maplibreGL(vtOpt("+STYLE+"));vt.addTo(map);s.width='';s.right='';map.invalidateSize()")
    pg.wait_for_timeout(1200)
    a=pg.evaluate(SZ);print('Größenwechsel beim Anlegen:',a);assert abs(a[0]-a[1])<=1 and abs(a[2]-a[3])<=1
    # Fenster wird nachträglich breiter (App/WebView)
    pg.set_viewport_size({'width':600,'height':900});pg.wait_for_timeout(1000)
    a=pg.evaluate(SZ);print('Fenster breiter:',a);assert abs(a[0]-a[1])<=1 and abs(a[2]-a[3])<=1
    b.close()
print('errors:',errs);sys.exit(1 if errs else 0)
