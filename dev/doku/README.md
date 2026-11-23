# Spielregeln (PDF) bauen

Zwei PDFs im Dossier-Stil, Seitenformat 90 × 160 mm (ein Handybildschirm pro Seite):
`Blown_Cover_Kurzanleitung.pdf` (9 S.) und `Blown_Cover_Spielregeln.pdf` (28 S.).

## Nur Text geändert
1. Text in `anleitung/content.py` ändern (`KURZ` = Kurzanleitung, `V` = Vollversion; Bausteine `page`, `item`, `side`, `fig`, `pair` …).
2. `python3 dev/doku/anleitung/build.py` → PDFs in `dev/out/anleitung/` (lädt beim ersten Mal die Schriften per `npm pack` nach `anleitung/fonts/`).
3. Prüfen: Seiten mit roter Umrandung laufen in die Fußzeile → Text kürzen oder Bild kleiner (`fig(…, w)`).
   Übersicht: `python3 dev/doku/anleitung/sheet.py dev/out/anleitung/Blown_Cover_Spielregeln.pdf /tmp/s.png 14`.
4. Inhaltsverzeichnis (`cover(…)`) und Seitenverweise (`S.&nbsp;20`) von Hand nachziehen, wenn sich Seiten verschieben.
5. Fakten immer im Code prüfen (`preOf(60)`, `tkInfo`, `shape`/`LG` usw.), nicht aus alten PDFs übernehmen.

## Screenshots neu erzeugen (nach App-Änderungen)
Die fertigen Ausschnitte liegen in `anleitung/img/` (im Repo, damit die PDFs ohne Kartenzugang baubar bleiben).
- Kartenkacheln gibt es nur mit `MAP=1` und erreichbarer Domain `tiles.openfreemap.org` (in der Cloud-Umgebung von Manuel freigegeben).
- `MAP=1 DSF=3 python3 dev/doku/screens.py dev/out/doku` – eigene Szenen (Hunter/Hider nach Ping, außerhalb der Zone, Fang melden, Bonuswahl) und alle Kartensymbole `sym_*.png` direkt aus `shape()`.
- Weitere Screens kommen aus Tests (`MAP=1 DSF=3 python3 dev/tests/<test>.py`, Ausgabe `dev/out/`): siehe Kommentare in `anleitung/ausschnitte.py`.
- `python3 dev/doku/anleitung/ausschnitte.py dev/out/doku dev/out` schneidet alles nach `anleitung/img/`.
- `dev/harness.py` blendet für Screenshots den Testmodus-Balken aus; `MAP=1` lässt MapLibre und die Kacheln durch.

## Gestaltung
`anleitung/base.css` (Raster, Bausteine) + `anleitung/dossier.css` (Behördenakte: IBM Plex Serif/Mono, Einstufung „GEHEIM“, Formular-Kopfzeile,
Lichtbilder mit zweiteiliger Büroklammer `img/klammer_vorne.svg`/`klammer_hinten.svg`, Papier `img/paper.jpg` aus `papier.py`).
