"""
Génère les icônes PWA KAPMAN depuis la DA (3 cercles additifs sur fond Ink).
Output : pwa/icon-192.png, pwa/icon-512.png, pwa/badge-72.png
100% local, aucune dépendance réseau.
"""
from pathlib import Path
from PIL import Image, ImageDraw

INK   = (13, 13, 13)      # #0D0D0D
RED   = (232, 55, 42)     # #E8372A
GREEN = (0, 166, 80)      # #00A650
BLUE  = (47, 87, 212)     # #2F57D4

OUT = Path(__file__).parent.parent / "pwa"
OUT.mkdir(parents=True, exist_ok=True)


def additive_blend(base, color, alpha):
    """Simule la lumière additive : on éclaircit vers la couleur."""
    return tuple(
        min(255, int(b + c * alpha))
        for b, c in zip(base, color)
    )


def make_icon(size, badge=False):
    """3 cercles additifs centrés. Si badge=True, monochrome cream (Android badge)."""
    # Supersampling x4 pour des bords lisses
    ss = 4
    S = size * ss
    img = Image.new("RGB", (S, S), INK)

    # Rayon et positions des 3 cercles (chevauchement façon logo)
    r = int(S * 0.26)
    cy = S // 2
    gap = int(r * 0.62)
    cx_mid = S // 2
    centers = [
        (cx_mid - gap, cy, RED),
        (cx_mid,       cy, GREEN),
        (cx_mid + gap, cy, BLUE),
    ]

    if badge:
        # Badge Android = silhouette monochrome (cream) sur transparent
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for cx, cyc, _ in centers:
            draw.ellipse([cx - r, cyc - r, cx + r, cyc + r], fill=(245, 240, 232, 255))
        img = img.resize((size, size), Image.LANCZOS)
        return img

    # Mode additif : on dessine chaque cercle en accumulant la lumière
    px = img.load()
    for cx, cyc, color in centers:
        for y in range(max(0, cyc - r), min(S, cyc + r)):
            dy = y - cyc
            half = int((r * r - dy * dy) ** 0.5) if r * r >= dy * dy else 0
            for x in range(max(0, cx - half), min(S, cx + half)):
                px[x, y] = additive_blend(px[x, y], color, 0.85)

    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    make_icon(192).save(OUT / "icon-192.png")
    make_icon(512).save(OUT / "icon-512.png")
    make_icon(72, badge=True).save(OUT / "badge-72.png")
    print(f"Icônes générées dans {OUT}")
    for f in ["icon-192.png", "icon-512.png", "badge-72.png"]:
        p = OUT / f
        print(f"  {f} — {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
