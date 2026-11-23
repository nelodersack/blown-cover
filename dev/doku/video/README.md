# Erklärvideo (1:52, 1080 × 1920, Dossier-Stil)

Echte App im Testaufbau (`dev/memdb.js`), Kartenkacheln von openfreemap, Stimme Piper „Thorsten“ (offline).
Arbeitsordner z. B. `dev/out/video` (nicht im Repo).

1. `pip install --break-system-packages piper-tts`, Stimme laden (siehe Kopf von `tts.py`).
2. Stimme: `BC_GTTS_KEY=<Schlüssel> python3 dev/doku/video/tts_google.py dev/out/video` (Google Chirp 3 HD „Charon“, Manuels Wahl) – offline-Ersatz: `python3 dev/doku/video/tts.py dev/out/video` – Sätze aus `narr.py` (Untertitel + Sprechfassung mit Lautschrift für englische Wörter).
3. `python3 dev/doku/video/scenes.py dev/out/video [s01 …]` – nimmt die Szenen auf (`frames/<szene>/`, CDP-Screencast, Aktionen nach den Satzzeiten).
4. Einmal `dev/out/video/paper_hd.jpg` erzeugen (Papier 1080 × 1920, siehe `papier_hd.py`).
5. `python3 dev/doku/video/compose.py dev/out/video` → `Blown_Cover_Erklaervideo.mp4` (Rahmen, Untertitel, Ton, ~4 Min).

Figuren: Hunter Anna (Host) und Ben, Hider Lena, Max, Tom, Sara; Graz, 60-Min-Voreinstellung.
Ändert sich die App (Texte, Panel, Abläufe), Szene neu aufnehmen und `compose.py` erneut laufen lassen.
Drehbuch: Doc „Blown Cover – Videoskript Erklärvideo“ (claude.ai).
