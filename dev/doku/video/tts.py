# Sprechertext → WAV je Satz (Piper, Stimme „Thorsten high“, offline). Aufruf: python3 dev/doku/video/tts.py <arbeitsordner>
# Stimme einmalig laden (GitHub-Release von sherpa-onnx, Hugging Face ist aus der Cloud oft gesperrt):
#   curl -L -o th.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-high.tar.bz2
#   tar xjf th.tar.bz2 -C <arbeitsordner>/voice   (dazu die .onnx.json aus rhasspy/piper-voices, liegt hier als thorsten-high.onnx.json)
import json, subprocess, sys, os, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from narr import S, speak
from piper import PiperVoice
from piper.config import SynthesisConfig
WORK = sys.argv[1]; D = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(WORK, 'tts'), exist_ok=True)
v = PiperVoice.load(os.path.join(WORK, 'voice/vits-piper-de_DE-thorsten-high/de_DE-thorsten-high.onnx'), config_path=os.path.join(D, 'thorsten-high.onnx.json'))
cfg = SynthesisConfig(length_scale=1.06, noise_scale=0.55, noise_w_scale=0.7)
meta = {}
for sc, sents in S.items():
    meta[sc] = []
    for i, t in enumerate(sents):
        fn = os.path.join(WORK, 'tts', f's{sc:02d}_{i}.wav')
        with wave.open(fn, 'wb') as w: v.synthesize_wav(speak(t), w, syn_config=cfg)
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fn], capture_output=True, text=True).stdout)
        meta[sc].append({'text': t, 'file': fn, 'dur': round(d, 3)})
json.dump(meta, open(os.path.join(WORK, 'tts', 'meta.json'), 'w'), ensure_ascii=False, indent=1)
for sc in meta: print(sc, round(sum(m['dur'] for m in meta[sc]), 1), 's')
