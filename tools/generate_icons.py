"""
Génère les icônes PWA CIRCUIT FERMÉ depuis la DA v4 (« la société d'écoute ») :
pastille carbone + sceau « CF » (Space Mono Bold, laiton) cerné d'un anneau
sillon fin, même motif que le sceau du header et de la carte de partage.
Output : pwa/icon-192.png, pwa/icon-512.png, pwa/badge-72.png
100% local, aucune dépendance réseau.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CARBONE = (10, 10, 12)     # #0A0A0C — fond (identique à --carbone)
LAITON = (194, 163, 107)   # #C2A36B — sceau + anneau (identique à --laiton)
WHITE = (255, 255, 255)    # badge monochrome (Android tinte lui-même l'icône)

FONTS = Path(__file__).parent / "assets" / "fonts"
OUT = Path(__file__).parent.parent / "pwa"
OUT.mkdir(parents=True, exist_ok=True)


def make_icon(size, badge=False, maskable_safe=False):
    """Sceau CF centré sur pastille carbone (ou transparent pour le badge).
    - badge=True   -> anneau + monogramme blancs sur fond transparent (badge
      Android monochrome, le système applique sa propre teinte).
    - maskable_safe=True -> motif contraint au cercle central de 80% du
      canvas (marge de sécurité pour les launchers qui recadrent en
      cercle/squircle)."""
    ss = 4  # supersampling pour bords lisses
    S = size * ss

    if badge:
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    else:
        img = Image.new("RGB", (S, S), CARBONE)
    draw = ImageDraw.Draw(img)

    safe_dim = S * 0.80 if maskable_safe else S
    color = WHITE if badge else LAITON

    cx = cy = S / 2
    ring_r = safe_dim * 0.36
    ring_width = max(2, round(S * 0.010))
    draw.ellipse(
        [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
        outline=color, width=ring_width,
    )

    f_cf = ImageFont.truetype(str(FONTS / "SpaceMono-Bold.ttf"), round(safe_dim * 0.30))
    cf_bbox = draw.textbbox((0, 0), "CF", font=f_cf)
    cf_w = cf_bbox[2] - cf_bbox[0]
    cf_h = cf_bbox[3] - cf_bbox[1]
    draw.text((cx - cf_w / 2 - cf_bbox[0], cy - cf_h / 2 - cf_bbox[1]), "CF", font=f_cf, fill=color)

    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    make_icon(192).save(OUT / "icon-192.png")
    make_icon(512, maskable_safe=True).save(OUT / "icon-512.png")
    make_icon(72, badge=True).save(OUT / "badge-72.png")
    print(f"Icônes générées dans {OUT}")
    for f in ["icon-192.png", "icon-512.png", "badge-72.png"]:
        p = OUT / f
        with Image.open(p) as im:
            dims = im.size
            mode = im.mode
        print(f"  {f} — {p.stat().st_size} octets — {dims[0]}x{dims[1]} — {mode}")


if __name__ == "__main__":
    main()
