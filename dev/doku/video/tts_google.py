# Sprechertext → WAV je Satz über Google Cloud Text-to-Speech (Chirp 3 HD, Stimme „Charon“).
# Aufruf: BC_GTTS_KEY=<API-Schlüssel> python3 dev/doku/video/tts_google.py <arbeitsordner> [stimme]
# Schlüssel nie ins Repo; Domain texttospeech.googleapis.com muss erreichbar sein. Kosten: ~1.300 Zeichen je Durchlauf.
import json, sys, os, base64, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from narr import S
WORK = sys.argv[1]; VOICE = sys.argv[2] if len(sys.argv) > 2 else 'Charon'
KEY = os.environ['BC_GTTS_KEY']
os.makedirs(os.path.join(WORK, 'tts'), exist_ok=True)
# Google liest englische Spielbegriffe richtig; nur wenige Ersetzungen
PH = []
def say(t):
    for a, b in PH: t = t.replace(a, b)
    return t
meta = {}
for sc, sents in S.items():
    meta[sc] = []
    for i, t in enumerate(sents):
        body = {"input": {"text": say(t)}, "voice": {"languageCode": "de-DE", "name": f"de-DE-Chirp3-HD-{VOICE}"},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000}}
        req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={KEY}", data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'})
        a = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))['audioContent'])
        fn = os.path.join(WORK, 'tts', f's{sc:02d}_{i}.wav'); open(fn, 'wb').write(a)
        # Stille am Anfang/Ende abschneiden, damit die Satzzeiten genau sind
        tmp = fn + '.t.wav'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', fn, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.05',
                        tmp], check=True)
        os.replace(tmp, fn)
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fn], capture_output=True, text=True).stdout)
        meta[sc].append({'text': t, 'file': fn, 'dur': round(d, 3)})
json.dump(meta, open(os.path.join(WORK, 'tts', 'meta.json'), 'w'), ensure_ascii=False, indent=1)
for sc in meta: print(sc, [m['dur'] for m in meta[sc]], round(sum(m['dur'] for m in meta[sc]), 1))
