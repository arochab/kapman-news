"""
Génère les icônes PWA CIRCUIT FERMÉ depuis la DA v5 (« Index de sélection ») :
cartouche RECTANGULAIRE noir plein portant « CF » en Inter Tight ExtraBold
ivoire, posé sur fond ivoire · le micro-signe du registre, jamais de cercle.
Output : pwa/icon-192.png, pwa/icon-512.png, pwa/badge-72.png
100% local, aucune dépendance réseau.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

IVOIRE = (252, 251, 247)   # #FCFBF7 · fond (identique à --ivoire)
NOIR = (18, 18, 18)        # #121212 · cartouche (identique à --noir)
WHITE = (255, 255, 255)    # badge monochrome (Android tinte lui-même l'icône)

FONTS = Path(__file__).parent / "assets" / "fonts"
OUT = Path(__file__).parent.parent / "pwa"
OUT.mkdir(parents=True, exist_ok=True)


def _cartouche_geometry(S, safe_dim):
    """Rectangle du cartouche + fonte CF, centrés dans la zone sûre."""
    box_w = safe_dim * 0.78
    box_h = safe_dim * 0.56
    cx = cy = S / 2
    rect = [cx - box_w / 2, cy - box_h / 2, cx + box_w / 2, cy + box_h / 2]
    font = ImageFont.truetype(str(FONTS / "InterTight-ExtraBold.ttf"), round(box_h * 0.60))
    return rect, font, cx, cy


def make_icon(size, maskable_safe=False):
    """Cartouche CF noir centré sur fond ivoire.
    - maskable_safe=True -> motif contraint au carré central de 80% du
      canvas (marge de sécurité pour les launchers qui recadrent en
      cercle/squircle)."""
    ss = 4  # supersampling pour bords lisses
    S = size * ss
    img = Image.new("RGB", (S, S), IVOIRE)
    draw = ImageDraw.Draw(img)

    safe_dim = S * 0.80 if maskable_safe else S * 0.92
    rect, f_cf, cx, cy = _cartouche_geometry(S, safe_dim)
    draw.rectangle(rect, fill=NOIR)

    cf_bbox = draw.textbbox((0, 0), "CF", font=f_cf)
    cf_w = cf_bbox[2] - cf_bbox[0]
    cf_h = cf_bbox[3] - cf_bbox[1]
    draw.text((cx - cf_w / 2 - cf_bbox[0], cy - cf_h / 2 - cf_bbox[1]), "CF", font=f_cf, fill=IVOIRE)

    return img.resize((size, size), Image.LANCZOS)


def make_badge(size):
    """Badge Android monochrome : silhouette du cartouche, blanc sur
    transparent, « CF » évidé (le système applique sa propre teinte)."""
    ss = 4
    S = size * ss
    alpha = Image.new("L", (S, S), 0)
    draw = ImageDraw.Draw(alpha)

    rect, f_cf, cx, cy = _cartouche_geometry(S, S * 0.96)
    draw.rectangle(rect, fill=255)

    cf_bbox = draw.textbbox((0, 0), "CF", font=f_cf)
    cf_w = cf_bbox[2] - cf_bbox[0]
    cf_h = cf_bbox[3] - cf_bbox[1]
    draw.text((cx - cf_w / 2 - cf_bbox[0], cy - cf_h / 2 - cf_bbox[1]), "CF", font=f_cf, fill=0)

    alpha = alpha.resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (size, size), WHITE + (0,))
    img.putalpha(alpha)
    return img


def main():
    make_icon(192).save(OUT / "icon-192.png")
    make_icon(512, maskable_safe=True).save(OUT / "icon-512.png")
    make_badge(72).save(OUT / "badge-72.png")
    print(f"Icônes générées dans {OUT}")
    for f in ["icon-192.png", "icon-512.png", "badge-72.png"]:
        p = OUT / f
        with Image.open(p) as im:
            dims = im.size
            mode = im.mode
        print(f"  {f} · {p.stat().st_size} octets · {dims[0]}x{dims[1]} · {mode}")


if __name__ == "__main__":
    main()
