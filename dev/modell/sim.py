"""Grobes Rechenmodell fürs Balancing (Monte-Carlo, eine Runde = viele Zufallsläufe).

Zweck: Besetzungen und Dauern VERGLEICHEN (wer ist im Vorteil?), nicht exakte Siegquoten vorhersagen.
Die Spielwerte kommen immer direkt aus balCalc in index.html (über die Testumgebung), damit Modell und
App nie auseinanderlaufen.

Ablauf einer Runde (Takt 10 s, Zeit ab Ende des Headstarts):
- Hider stehen zufällig in der Zone (bis 85 % des Startradius), Hunter starten in der Mitte.
- Ping: Hunter erfahren die Standorte aller freien Hider. Jeder Hunter nimmt den nächsten noch nicht
  gewählten Hider (bei mehr Huntern als Hidern teilen sie sich Ziele) und geht dorthin.
- Hider ziehen nach einem Ping mit Wahrscheinlichkeit UMZ bis zu 200 m um (Pings sind bekannt).
- Sieht ein Hunter einen Hider (Abstand < SICHT, pro Takt Wahrscheinlichkeit P_SEH wegen Deckung),
  fängt er ihn pro Takt mit Wahrscheinlichkeit P_FANG (Verfolgung/Festsetzen). Bemerkt ein Hider einen
  Hunter (< 120 m), läuft er weg.
- Die Zone schrumpft wie in der App; Hider außerhalb gehen nach innen.
- Hunter gewinnen, wenn alle Hider gefangen sind; sonst die Hider.
Nicht im Modell: Aufgaben, Boni, Hider-Pings, Gelände. Geeicht wird die Sichtweite (Deckung, Gelände) so, dass 2 Hunter / 4 Hider bei 30 Min
mit den Voreinstellungen etwa 50 % ergibt (Ziel aus dem Balancing-Konzept).

Aufruf: python3 dev/modell/sim.py [läufe]          → Tabelle für typische Besetzungen
        python3 dev/modell/sim.py 400 8/12 6/14    → nur diese Besetzungen (30 und 60 Min)
"""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app

DT = 10                      # Takt in s
V_H, V_H_JAGD = 1.5, 3.0     # Hunter gehen / rennen (m/s)
V_X, V_X_FLUCHT = 1.3, 2.8   # Hider gehen / flüchten
SICHT, P_SEH, P_FANG = 40, 0.5, 0.5
MERK, UMZ = 120, 0.5
EICH = 1.0                   # Eichfaktor auf die Sichtweite SICHT (siehe eichen())


def werte(cfgs, k=2):
    """balCalc-Ergebnisse aus der echten App holen: cfgs = [(mode,H,X,T)]."""
    js = json.dumps(cfgs)
    with app() as (pg, ev, errs):
        pg.wait_for_timeout(300)
        return ev("""(()=>%s.map(([mode,H,X,T])=>{const s=Object.assign({},DEF,PRE[T]||PRE[30],{dur:T,mode});return balCalc(s,H,X,%d).o}))()""" % (js, k))


def radius(o, t):
    n = int(t // (o['shrink'] * 60))
    return max(o['rMin'], o['r0'] - n * o['step'])


def runde(o, H, X, T, rng, eich=EICH):
    r0 = o['r0']; ping = o['ping']; dauer = T * 60 - o['head'] * 60
    a = rng.uniform(0, 2 * np.pi, X); d = r0 * 0.85 * np.sqrt(rng.uniform(0, 1, X))
    xs = np.c_[d * np.cos(a), d * np.sin(a)]; frei = np.ones(X, bool)
    hs = np.zeros((H, 2)); ziel = np.zeros((H, 2)); hz = -np.ones(H, int)
    xziel = xs.copy(); pf = P_FANG; SI = SICHT * eich
    t = 0.0; nextp = 0.0
    while t < dauer:
        r = radius(o, t + o['head'] * 60)
        if t >= nextp:
            nextp += ping
            idx = np.flatnonzero(frei)
            if idx.size:
                genommen = set()
                for h in range(H):
                    dist = np.linalg.norm(xs[idx] - hs[h], axis=1)
                    order = np.argsort(dist); w = next((i for i in order if idx[i] not in genommen), order[0])
                    genommen.add(idx[w]); hz[h] = idx[w]; ziel[h] = xs[idx[w]]
                # Hider ziehen nach dem Ping um
                um = frei & (rng.uniform(0, 1, X) < UMZ)
                for i in np.flatnonzero(um):
                    for _ in range(5):
                        p = xs[i] + rng.uniform(-200, 200, 2)
                        if np.linalg.norm(p) < 0.9 * r: xziel[i] = p; break
        # Sicht / Fang
        D = np.linalg.norm(hs[:, None, :] - xs[None, :, :], axis=2); D[:, ~frei] = 1e9
        seen = (D < SI) & (rng.uniform(0, 1, D.shape) < P_SEH)
        for h in range(H):
            js_ = np.flatnonzero(seen[h])
            if js_.size:
                j = js_[np.argmin(D[h, js_])]; ziel[h] = xs[j]; hz[h] = j
                if rng.uniform() < pf: frei[j] = False
        if not frei.any(): return False
        # Hunter bewegen
        for h in range(H):
            dv = ziel[h] - hs[h]; dn = np.linalg.norm(dv)
            jagd = hz[h] >= 0 and frei[hz[h]] and np.linalg.norm(xs[hz[h]] - hs[h]) < SI * 2
            v = (V_H_JAGD if jagd else V_H) * DT
            if dn < 15:   # angekommen, nichts gesehen: in der Nähe suchen
                ziel[h] = hs[h] + rng.uniform(-100, 100, 2)
            else:
                hs[h] += dv / dn * min(v, dn)
        # Hider bewegen: Flucht, Zone, Umzug
        for i in np.flatnonzero(frei):
            dh = np.linalg.norm(hs - xs[i], axis=1); m = np.argmin(dh)
            if dh[m] < MERK and rng.uniform() < 0.5:
                dv = xs[i] - hs[m]; dv /= (np.linalg.norm(dv) + 1e-9); xs[i] += dv * V_X_FLUCHT * DT; xziel[i] = xs[i].copy()
            else:
                dv = xziel[i] - xs[i]; dn = np.linalg.norm(dv)
                if dn > 1: xs[i] += dv / dn * min(V_X * DT, dn)
            n = np.linalg.norm(xs[i])
            if n > r: xs[i] *= (r * 0.95) / n; xziel[i] = xs[i].copy()
        t += DT
    return True   # mindestens ein Hider übrig


def quote(o, H, X, T, n, seed=1, eich=EICH):
    rng = np.random.default_rng(seed)
    return sum(runde(o, H, X, T, rng, eich) for _ in range(n)) / n


def eichen(n=300):
    """Sichtweite so skalieren, dass 2/4 bei 30 Min mit den Voreinstellungen ~50 % Hider-Siege ergibt."""
    o = werte([('survive', 2, 4, 30)])[0]; lo, hi = 0.25, 6.0
    for _ in range(9):
        m = math.sqrt(lo * hi); q = quote(o, 2, 4, 30, n, eich=m)
        lo, hi = (m, hi) if q > 0.5 else (lo, m)
    return math.sqrt(lo * hi)


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    bes = [tuple(map(int, a.split('/'))) for a in sys.argv[2:]] or [(1, 3), (2, 4), (2, 6), (3, 6), (4, 4), (4, 12), (5, 15), (6, 14), (7, 13), (8, 12)]
    e = eichen(); print('Eichung: Sichtweite %.0f m (2/4, 30 Min ≈ 50 %%)' % (SICHT * e))
    cfg = [('survive', H, X, T) for H, X in bes for T in (30, 60)]
    ws = werte(cfg)
    print('Besetzung  Dauer  Zone         Ping   Pings  Hider-Siege')
    for (m, H, X, T), o in zip(cfg, ws):
        q = quote(o, H, X, T, n, eich=e)
        print('%2d/%-2d     %3d    %4d→%-4d  %4ds  %5.1f  %5.0f %%' % (H, X, T, o['r0'], o['rMin'], o['ping'], (T - o['head']) * 60 / o['ping'], q * 100))
