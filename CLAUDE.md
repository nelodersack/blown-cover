# Blown Cover – Arbeitsanleitung für Claude

IRL-Versteckspiel (Hunter gegen Hider, schrumpfende GPS-Zone, Pings, Aufgaben). Die gesamte Web-App steckt in **`index.html`** (≈210 KB, Leaflet + Firebase Realtime DB europe-west1). `main` ist über GitHub Pages live: https://nelodersack.github.io/blown-cover/. Die Android-App (Zweig `android-app`) ist eine WebView-Hülle und lädt die Live-Seite. Website-Änderungen brauchen deshalb keine neue APK, außer die Bridge `BlownNative` oder Java-Code ändert sich.
Mit Manuel auf Deutsch sprechen, knapp und direkt.

## Sparsam lesen (wichtig)
- **`index.html` nie ganz lesen.** Erst `grep -n "§" index.html` ausführen (Abschnittsmarken mit Zeilennummern), dann mit `Read` und `offset`/`limit` nur den Abschnitt lesen.
- Funktionen findest du mit `grep -n "function name\|const name=" index.html`. Viele Zeilen sind lang und dicht: lieber `grep -o ".\{80\}stichwort.\{120\}"` als ganze Zeilen.
- Historie und Begründungen stehen in `CHANGELOG.md`. Nur lesen, wenn es nötig ist.
- Der Projektstand für andere Chats liegt im claude.ai-Projekt „Blown Cover“: `claude/UEBERGABE_App.md` (kurz). Konzepte: `claude/KONZEPT_Hacking.md`, `KONZEPT_Balancing.md`, `KONZEPT_Zombie.md`.

## Codekarte (`grep -n "§" index.html`)
CSS: `§CSS-BASIS` (Tokens `--task` lila, `--danger`, `--ok`, `--xping`), `§CSS-ELEMENTE`, `§CSS-KOMPONENTEN` (card, chip, acc, `.fl`/`.fl.sub`, num, sw), `§CSS-OVERLAYS`, `§CSS-CHAT`, `§CSS-DIALOG`, `§CSS-REPLAY`, `§CSS-KNOEPFE`. `§HTML` Grundgerüst.
JS in Dateireihenfolge:
| Marke | Inhalt / wichtige Namen |
|---|---|
| §INIT | Firebase-Config, `NB` (App-Bridge), `TEST` (`#test` im URL-Hash), `LS` |
| §ANALYSE / §ANALYSE-DATEI | Protokoll `lg()`, `AL`; Analyse-JSON `anBuild`, `anDl`, `wfHarmless` |
| §APP | Sichtbarkeit, Fehler-Hooks, `bcSetHidden` |
| §STATE | globale `let`s (G, uid, code, pos, ping, …), `now()` (Serverzeit), `$`, `esc`, `D` (Distanz m), `P()` (Spieler), `gwE`, `dqOn`, `hpOn`, `evW`, `note` |
| §ERGEBNIS | `CW`, `catchWhy`, `buildRes`, `resHTML`, `resSync` |
| §ZONE-AUFGABEN-RECHNUNG | `rs` (Ende Headstart), `Rad(g,t)`, `zoneSeq`, `md(g)` (Modus), `ddPlan`, Boni `hb*`, `myTk`, `myItems`, Orte `ovPts`/`randPts`/`mkPts` |
| §UI-BASIS | `toast`, Icons `SV`/`ic()`, Farben `PAL`/`colOf`, Markerformen `shape`/`shape0`, `TH`, Wake Lock |
| §KARTE, §KARTE-DREHEN, §AUSRICHTUNG, §GESTEN, §KOMPASS | `map`, `rotSize`, `fitZ`, `FM`/`FA`, `nbTap`, Gesten `g*`, Blickrichtung `HD`, `crs` |
| §REPLAY-AUFNAHME | `RP`, `rpLog`, `rpSnap`, `rpBuild`, `rpDl` |
| §REPLAY | `rv*`: `rvConv`, `rvScan` (Ereignisse), `rvStats`, `rvDraw`, `rvTaskShow`, `rvPanel` |
| §GPS | `startGPS`, `write` |
| §JOIN | `mk` (Spiel erstellen), `join`, `appReady` |
| §DIALOG | `dlg({t,x,…})` – alle Dialoge im App-Design, nie `alert/confirm` |
| §FARBWAHL, §MARKER | Spielerfarbe; eigene Kartenmarker `mk*`, `drawMarks` |
| §LOBBY-AKTIONEN | `setRole`, `setS(k,v,min,max)`, `setMode`, `giveUp`, `leaveGame`, `newRound`, Spielstart `st` |
| §FANG | `cc`, `rq`, `ok`, `no`, `fin`, `endNow` |
| §AUFGABEN | Hunter-Boni `hb*`, Meeting `mt*`, `chk`, Evakuierung `rv*`-Lock, `useImm`, `hTasks`, Zuschauer `specView`, Radar, `hInv` |
| §CHAT, §PANEL-ZIEHEN | Chat `ch*`; Panel-Geste |
| §EINSTELLUNGEN | `ui`, `DEF`, **`FD`** (Feld-Definitionen), `PRE` (Dauer-Presets), `setPre`, `setHk` |
| §BALANCING | `balCalc`, `balAcc`, `balGo` |
| §LOBBY-UI | `nf(k,sub)`, `swt(k,on,label,sub,sub?)`, `acc(...)`, `lobbyUI` |
| §RUN-UI, §PANEL | `runUI`, `panel(force)` (rendert nur bei geänderter Signatur `lastSig`) |
| §HACKING | `hkDef`, `hkSt`, `hkAct`, `hkProg`, `hkTick`, `hkJoin/Leave`, `hkCmUse`, `oz*`, `liveNow`, `hkHCard`, `hkHunterCard`, `hkDraw`, `hkSig` |
| §ZEICHNEN | `draw()` (alle Karten-Layer), `mkr` (Marker mit Popup), `tkInfo` (Aufgaben-Popup: Name + Belohnung, auch im Replay), Legende `LG` |
| §ONDATA | `onData()` nach jeder DB-Änderung |
| §TICK | `setInterval` 1 s: HUD, GPS-/Netz-Warnung, Zone, Pings, Fänge, Spielende |
| §BOOT | Anmeldung, Wiedereinstieg |

Eine neue Marke bekommt eine eigene Zeile `// §NAME kurze Beschreibung` (CSS: `/* §CSS-NAME */`). Die Tabelle oben dann mitpflegen.

## Datenmodell (Firebase)
- `games/$code`: `host`, `status` (lobby|running|over), `startAt`, `winner`, `c` {lat,lng} (Zonenmitte), `rn` (Rundennummer), `prev`, `chk`
  - `s` Einstellungen (siehe unten). `players/$uid`: name, role (hunter|hider), state (alive|caught|dq|safe|…), lat, lng, ts, j, col, out, revealUntil, immUntil, used, sT, lf, w, oa
  - `catches/$hider` {hunter,t,status,why}, `hb/$hunter/$bonus`, `live/$hider/$hunter`, `xp/$id` (Extra-Ping), `ev/$id` {t,x,u} (Meldungen an alle; `u:'hk'` = Hacking-System)
  - `tasks/$tid`: `sh` (Safehouse), `ev` (Evakuierung), Dead Drops/Meetings (`isDd(id)`), `hk` (Hacking: `t0`, `loc`, `rr:0`, `at/<n>` Versuche, `res`, `cm`, `oz`; `a` ist bei Dead Drop belegt, darum heißt der Versuchsknoten `at`)
- `chats/…`, `marks/…`, `analysis/$code` (Analyse-Protokolle), `rp/$code/$uid` (Replay-Wege)
- **Regeln:** `database.rules.json` liegt im Zweig `db-rules` (`git show db-rules:database.rules.json`). Unter `s`, `players/$pid` usw. gilt `$o: false`: **jede neue Einstellung bzw. jedes neue Feld braucht eine Regel**, sonst schlägt das Schreiben fehl. Claude liefert Manuel immer die komplette Datei, Manuel lädt sie selbst hoch. Danach den Zweig `db-rules` aktualisieren.

## Einstellungen (`G.s`)
Zahlen stehen in `FD` als `key:[Label,min,max,Schritt,Einheit]`: r0, rMin, shrink, step, ot, head, dur, ping, pen, gw, gd, shT, imm, ddN, ddT, mtN, mtT, taskR, evT, hbN, hbC, hbL, hbT, hkS, hkZ, hkT, hkR, hkN, ozR. Schalter: mode (survive|mission), shOn, bon, hbOn, an (Analyse), dq, hp, rp, hk.
Eine neue Einstellung braucht: `FD` (oder Schalter), Standardwert (`DEF`/`PRE`/`hkDef`), Zeile in `lobbyUI` (Unterpunkt mit `nf(k,1)`), DB-Regel `s/<key>`, ggf. `balCalc`.

## Konventionen
- Zeit immer über `now()` (Serverzeit-Offset), nicht `Date.now()` für Spielzeit.
- Jeder Client prüft gemeinsame Ereignisse selbst (Spielende, Fang-Timeout, Hacking-Versuchsende); das erste gültige Schreiben gewinnt, Locks wie `endLock` verhindern Doppel-Schreiben.
- `panel()` rendert nur bei geänderter Signatur neu. Neue Zustände, die das Panel ändern, gehören in die Signatur (z. B. `hkSig`).
- Aufgaben sind lila (`var(--task)` #7c6cff), Fang rot, Boni blau, Sichtbarkeit/Strafe orange (pulsierend).
- Testmodus `#test`: Positionen per Kartenklick, `sessionStorage`, keine Signal-DQ durch andere.

## Testen
- `sh dev/check.sh` prüft die JS-Syntax und führt alle Tests in `dev/tests/` aus. `sh dev/check.sh syntax` prüft nur die Syntax, `sh dev/check.sh replay` führt nur passende Tests aus.
- Die Tests laufen mit Playwright/Chromium (vorinstalliert) und `dev/memdb.js` als Firebase-Ersatz: `__T` ist die Datenbank, `notify()` löst die Listener aus. Vorlage für neue Tests: `dev/tests/hacking_mit_helfer.py` (Spiel in `__T.games` anlegen, `uid`/`pos` setzen, `join(code)`). Screenshots landen in `dev/out/` (nicht im Repo).
- Firebase und github.io sind aus der Cloud-Umgebung nicht erreichbar. Echte Tests macht Manuel auf dem Handy und schickt Analyse-JSON bzw. App-Logs.

## Regeln von Manuel
- **Nichts nach `main` ohne sein ausdrückliches Wort.** Erst auf einen Zweig pushen (mit `-u`), nach „Go“ per Fast-Forward auf `main`. Zweige löscht Manuel selbst.
- „Go“ vor Konzept-Features. Alle Dialoge im App-Design. Mockups aus echtem App-CSS. Das Design nur ändern, wenn er es will.
- **Nach jeder Repo-Änderung:** einen Eintrag in `CHANGELOG.md` anhängen und sofort `claude/UEBERGABE_App.md` im Projekt aktualisieren (Commit-Stand, Offen). Vorher die aktuelle Fassung lesen, weil andere Chats die Datei auch schreiben.
- APK bauen und auf dem Gerät testen macht Manuel. Kein Android-SDK in der Umgebung (javac gegen android.jar aus `Sable/android-platforms`).
- Commit-Nachrichten auf Deutsch.

## Zweige
`main` (live), `android-app` (App, `android/`, Workflow baut APK als Artifact `BlownCover-APK`), `db-rules` (nur `database.rules.json`). Signaturschlüssel liegen nur in den GitHub-Secrets.
