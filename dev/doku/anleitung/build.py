# Baut die Spielregeln als PDF im Dossier-Stil: Kurzanleitung + Vollversion.
# Aufruf: python3 dev/doku/anleitung/build.py [zielordner]   (Standard: dev/out/anleitung)
# Braucht google-chrome (headless) und einmalig npm für die Schriften (IBM Plex, OFL).
import subprocess, sys, pathlib, shutil
D = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(D))
import content as C

FONTS = D / "fonts"
PKGS = {"fontsource-ibm-plex-serif": "@fontsource/ibm-plex-serif", "fontsource-ibm-plex-mono": "@fontsource/ibm-plex-mono"}

def fonts():
    FONTS.mkdir(exist_ok=True)
    for d, pkg in PKGS.items():
        if (FONTS / d).exists(): continue
        tgz = subprocess.run(["npm", "pack", pkg, "--silent"], cwd=FONTS, check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1]
        subprocess.run(["tar", "xzf", tgz], cwd=FONTS, check=True)
        shutil.move(str(FONTS / "package"), str(FONTS / d)); (FONTS / tgz).unlink()

def css():
    t = (D / "dossier.css").read_text().replace("IMG/", str(D / "img") + "/").replace("FONTS/", str(FONTS) + "/")
    return (D / "base.css").read_text() + t

# Markiert Seiten, deren Inhalt in die Fußzeile läuft (rote Umrandung im PDF)
CHECK = """<script>window.addEventListener('load',()=>{document.querySelectorAll('.page:not(.cover)').forEach(p=>{
const b=p.querySelector('.body');const r=b.getBoundingClientRect(),pr=p.getBoundingClientRect();
if(r.bottom>pr.bottom-11*3.78)p.classList.add('overflow');});});</script>"""

def build(pages, name, title, out):
    html = f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>{title}</title><style>{css()}</style></head><body class="dossier">{"".join(pages)}{CHECK}</body></html>'
    h = out / f"{name}.html"; h.write_text(html)
    pdf = out / f"{name}.pdf"
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--no-pdf-header-footer",
                    "--virtual-time-budget=4000", f"--print-to-pdf={pdf}", f"file://{h}"], check=True, capture_output=True)
    print(pdf)

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else D.parent.parent / "out" / "anleitung"
    out.mkdir(parents=True, exist_ok=True); fonts()
    build(C.KURZ, "Blown_Cover_Kurzanleitung", "Blown Cover – Kurzanleitung", out)
    build(C.V, "Blown_Cover_Spielregeln", "Blown Cover – Spielregeln", out)
