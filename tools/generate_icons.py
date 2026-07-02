"""
Génère les icônes PWA KAPMAN SIGNAL depuis la DA (glyphe signal : 3 barres
verticales arrondies R/V/B, hauteurs 12/22/17, alignées en bas).
Output : pwa/icon-192.png, pwa/icon-512.png, pwa/badge-72.png
100% local, aucune dépendance réseau.
"""
from pathlib import Path
from PIL import Image, ImageDraw

INK   = (14, 15, 20)      # #0E0F14
RED   = (232, 58, 46)     # #E83A2E
GREEN = (31, 200, 94)     # #1FC85E
BLUE  = (58, 108, 240)    # #3A6CF0
WHITE = (255, 255, 255)   # badge monochrome

OUT = Path(__file__).parent.parent / "pwa"
OUT.mkdir(parents=True, exist_ok=True)

# Proportions du glyphe (unités relatives, référence hauteurs 12/22/17 sur une
# barre de largeur 6 -> ratio largeur/hauteur-max = 6/22).
BAR_H_RATIO = [12 / 22, 22 / 22, 17 / 22]  # r, g, b — hauteurs relatives à la barre la plus haute
BAR_W_TO_MAXH_RATIO = 6 / 22               # largeur d'une barre / hauteur max
GAP_TO_MAXH_RATIO = 5 / 22                 # espace entre barres / hauteur max


def draw_glyph(draw, cx, cy_bottom, max_h, colors, radius_ratio=0.5):
    """Dessine les 3 barres arrondies, alignées en bas sur cy_bottom, centrées sur cx.
    max_h = hauteur (en px) de la barre la plus haute (la verte)."""
    bar_w = max_h * BAR_W_TO_MAXH_RATIO
    gap = max_h * GAP_TO_MAXH_RATIO
    total_w = bar_w * 3 + gap * 2
    x0 = cx - total_w / 2
    for i, (ratio, color) in enumerate(zip(BAR_H_RATIO, colors)):
        h = max_h * ratio
        x_left = x0 + i * (bar_w + gap)
        x_right = x_left + bar_w
        y_top = cy_bottom - h
        y_bottom = cy_bottom
        radius = bar_w * radius_ratio
        draw.rounded_rectangle(
            [x_left, y_top, x_right, y_bottom],
            radius=radius,
            fill=color,
        )


def make_icon(size, badge=False, maskable_safe=False):
    """Glyphe signal centré sur fond ink. Largeur totale du glyphe ~= 45% du canvas.
    - badge=True   -> barres blanches sur fond transparent (badge Android monochrome).
    - maskable_safe=True -> motif contraint au cercle central de 80% du canvas
      (marge de sécurité maskable, pour les launchers qui recadrent en cercle/squircle)."""
    ss = 4  # supersampling pour bords lisses
    S = size * ss

    if badge:
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    else:
        img = Image.new("RGB", (S, S), INK)
    draw = ImageDraw.Draw(img)

    # Largeur totale visée : 45% du canvas (ou du cercle de sécurité maskable).
    safe_dim = S * 0.80 if maskable_safe else S
    target_total_w = safe_dim * 0.45
    # total_w = max_h * (3*BAR_W_TO_MAXH_RATIO + 2*GAP_TO_MAXH_RATIO)
    unit = 3 * BAR_W_TO_MAXH_RATIO + 2 * GAP_TO_MAXH_RATIO
    max_h = target_total_w / unit

    cx = S / 2
    cy_bottom = S / 2 + max_h / 2  # glyphe centré verticalement autour du milieu du canvas

    colors = [WHITE] * 3 if badge else [RED, GREEN, BLUE]
    draw_glyph(draw, cx, cy_bottom, max_h, colors)

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
