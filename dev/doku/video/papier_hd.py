# Papierstruktur 1080 × 1920 für das Video. Aufruf: python3 dev/doku/video/papier_hd.py <arbeitsordner>
import sys, os, numpy as np
from PIL import Image, ImageFilter
W, H = 1080, 1920; rng = np.random.default_rng(11); base = np.array([241, 237, 227], float)
def up(a, blur=0):
    im = Image.fromarray(((a * .25 + .5).clip(0, 1) * 255).astype('uint8')).resize((W, H), Image.BICUBIC)
    return np.array(im.filter(ImageFilter.GaussianBlur(blur)) if blur else im, float) / 255 - .5
f = np.array(Image.fromarray(((rng.normal(0, 1, (H, W)) * .5 + .5).clip(0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.7)), float) / 255 - .5
lo = up(rng.normal(0, 1, (H // 60, W // 60))); fib = up(rng.normal(0, 1, (H // 3, W // 18)), 1.5)
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * .45) / (H / 2)) ** 2); vig = np.clip(r - .75, 0, 1) * 22
img = base[None, None, :] + (f * 7 + lo * 7 + fib * 4)[..., None] * np.array([1, .95, .85]) - vig[..., None] * np.array([.9, 1, 1.3])
Image.fromarray(img.clip(0, 255).astype('uint8')).save(os.path.join(sys.argv[1], 'paper_hd.jpg'), quality=90)
