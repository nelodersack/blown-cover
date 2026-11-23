# Erzeugt img/paper.jpg (Papierstruktur der Dossier-Seiten, 90 x 160 mm bei 180 dpi). Einmalig, Ergebnis liegt im Repo.
import numpy as np, os
from PIL import Image, ImageFilter
W, H = 638, 1134; rng = np.random.default_rng(7); base = np.array([241, 237, 227], float)
def blur(a, s, r=0): 
    im = Image.fromarray(((a * .25 + .5).clip(0, 1) * 255).astype('uint8')).resize((W, H), Image.BICUBIC)
    return np.array(im.filter(ImageFilter.GaussianBlur(r)) if r else im, float) / 255 - .5
n = rng.normal(0, 1, (H, W)); f = np.array(Image.fromarray(((n * .5 + .5).clip(0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.6)), float) / 255 - .5
lo = blur(rng.normal(0, 1, (H // 40, W // 40)), 0); fib = blur(rng.normal(0, 1, (H // 2, W // 12)), 0, 1)
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * .45) / (H / 2)) ** 2); vig = np.clip(r - .8, 0, 1) * 14
img = base[None, None, :] + (f * 8 + lo * 6 + fib * 4)[..., None] * np.array([1, .95, .85]) - vig[..., None] * np.array([.9, 1, 1.3])
Image.fromarray(img.clip(0, 255).astype('uint8')).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'paper.jpg'), quality=82)
