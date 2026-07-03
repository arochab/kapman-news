"""
Génère la carte de partage (Open Graph, 1200x630) d'une issue CIRCUIT FERMÉ.

  python tools/og_card.py --content content/10.json

Rendu direct avec Pillow (pas de navigateur headless) à partir des mêmes
polices que le site (Fraunces, Space Grotesk, Space Mono, committées
localement dans tools/assets/fonts/ · aucun téléchargement au build CI) et
des mêmes couleurs de marque que templates/issue.html.j2 (charte v4, « la
société d'écoute »).

Composition : pochette / carte de membre, pas une bannière web. Fond
carbone, sillon (arcs concentriques hairline, 3 dans le métal de l'édition)
centré derrière le numéral filigrane, pastille métal + label d'édition,
tagline en Fraunces italique, sceau CF en haut à gauche, ligne mono en pied,
le tout cerné d'un bord hairline façon carte gaufrée.

Sortie : issues/NN/card.png. Appelé depuis tools/build_issue.py à chaque
rendu d'issue (import direct). Toute erreur (Pillow absent, police absente,
JSON incomplet) est capturée par l'appelant : le build ne doit jamais
échouer à cause d'une carte de partage manquante.
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
FONTS = Path(__file__).parent / "assets" / "fonts"
CONTENT = ROOT / "content"
ISSUES = ROOT / "issues"

# ── Dimensions Open Graph standard ──
W, H = 1200, 630

# ── Couleurs de marque (identiques à templates/issue.html.j2 :root, charte v4) ──
CARBONE = (10, 10, 12)      # #0A0A0C — fond
GRAPHITE = (19, 19, 22)     # #131316 — surfaces / filigrane du numéral
HAIRLINE = (38, 38, 43)     # #26262B — filets 1px
OS = (236, 231, 220)        # #ECE7DC — texte principal
BRUME = (156, 151, 138)     # #9C978A — texte secondaire
CREUSE = (110, 106, 96)     # #6E6A60 — méta discrète (≥12px / uppercase)
LAITON = (194, 163, 107)    # #C2A36B — accent
TERRACOTTA = (201, 108, 90)  # #C96C5A — erreurs uniquement (non utilisé ici)

# Cycle des éditions par issue_num % 3 — MÊME mécanique que templates/issue.html.j2
# (--issue-accent) et build_issue.py (build_row_html : accent_idx = issue_num % 3).
# 0 = laiton « OR », 1 = cuivre, 2 = acier.
METALS = [
    ("OR", (194, 163, 107)),      # laiton #C2A36B
    ("CUIVRE", (192, 141, 110)),  # cuivre #C08D6E
    ("ACIER", (169, 174, 184)),   # acier #A9AEB8
]

DASH_RE = re.compile(r"\s*[—–]\s*")


def no_dash(text: str) -> str:
    """Aucun tiret (— / –) dans un texte rendu : remplacé par ' · ' (règle éditoriale)."""
    if not text:
        return text
    return DASH_RE.sub(" · ", text).strip()


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> list[str]:
    """Word-wrap simple sur la largeur max_width, tronque proprement à max_lines
    (ajoute … sur la dernière ligne si le texte dépasse)."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
        if len(lines) == max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)

    if len(lines) == max_lines:
        # Vérifie si le texte restant a été coupé : ajoute une ellipse.
        consumed = " ".join(lines)
        if len(consumed) < len(text.rstrip()) and not consumed.endswith("…"):
            last = lines[-1]
            while draw.textlength(last + "…", font=font) > max_width and len(last) > 1:
                last = last[:-1].rstrip()
            lines[-1] = last + "…"
    return lines


def _row_date(date_iso: str) -> str:
    """date_iso 'YYYY-MM-DD' -> 'JJ.MM.AA' (même format que la home)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", date_iso or "")
    if not m:
        return date_iso or ""
    yyyy, mm, dd = m.groups()
    return f"{dd}.{mm}.{yyyy[2:]}"


def _tracked(text: str, spacing: str = " ") -> str:
    """Simule le letter-spacing large de la version web pour un rendu mono."""
    return spacing.join(text)


def _radial_mask(w: int, h: int, cx: int, cy: int, inner_r: int, outer_r: int) -> Image.Image:
    """Masque L (0..255) : opaque dans inner_r, dégradé jusqu'à 0 à outer_r.
    Calculé à basse résolution puis remis à l'échelle (pas de numpy) pour
    un fondu propre du sillon, sans bord de découpe visible."""
    lw, lh = 160, 84
    small = Image.new("L", (lw, lh), 0)
    px = small.load()
    scale_x, scale_y = w / lw, h / lh
    scx, scy = cx / scale_x, cy / scale_y
    sinner, souter = inner_r / scale_x, outer_r / scale_x
    for j in range(lh):
        for i in range(lw):
            d = ((i - scx) ** 2 + (j - scy) ** 2) ** 0.5
            if d <= sinner:
                v = 255
            elif d >= souter:
                v = 0
            else:
                v = round(255 * (1 - (d - sinner) / (souter - sinner)))
            px[i, j] = v
    return small.resize((w, h), Image.BICUBIC)


def _draw_sillon(img: Image.Image, cx: int, cy: int, accent: tuple):
    """Le sillon : arcs concentriques hairline centrés sur (cx, cy), 3 anneaux
    dans le métal de l'édition mêlés aux autres en hairline. Dessiné sur un
    calque à part puis fondu dans le fond avec un masque radial, pour que le
    motif se dissolve avant d'atteindre la tagline (cadré comme le hero
    d'issue : le numéral en spindle, le sillon en label de disque, pas un
    filigrane qui traverse tout le texte)."""
    layer = Image.new("RGB", img.size, CARBONE)
    ldraw = ImageDraw.Draw(layer)
    radii = range(90, 950, 80)
    accent_at = {150, 390, 630}  # 3 anneaux dans le métal, répartis sur la portée visible
    for r in radii:
        bbox = [cx - r, cy - r, cx + r, cy + r]
        closest = min(abs(a - r) for a in accent_at)
        if closest < 40:
            ldraw.ellipse(bbox, outline=accent, width=2)
        else:
            ldraw.ellipse(bbox, outline=HAIRLINE, width=1)
    mask = _radial_mask(img.width, img.height, cx, cy, inner_r=230, outer_r=470)
    img.paste(layer, (0, 0), mask)


def _draw_seal(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, f_cf: ImageFont.FreeTypeFont):
    """Sceau CF : cercle hairline + monogramme Space Mono Bold centré."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=HAIRLINE, width=2)
    cf_bbox = draw.textbbox((0, 0), "CF", font=f_cf)
    cf_w = cf_bbox[2] - cf_bbox[0]
    cf_h = cf_bbox[3] - cf_bbox[1]
    draw.text((cx - cf_w / 2 - cf_bbox[0], cy - cf_h / 2 - cf_bbox[1]), "CF", font=f_cf, fill=OS)


def render_card(content: dict) -> Image.Image:
    issue_num = content["issue_num"]
    metal_name, metal_color = METALS[issue_num % 3]

    img = Image.new("RGB", (W, H), CARBONE)

    margin = 64

    # ── Le sillon, centré au delà du coin haut droit (coeur hors cadre) :
    # le numéral devient le spindle du disque, les anneaux le label ; le
    # fondu radial l'éteint bien avant la tagline. Dessiné avant tout le
    # reste (paste sur l'image nue), puis draw est lié une seule fois. ──
    _draw_sillon(img, cx=W + 60, cy=110, accent=metal_color)
    draw = ImageDraw.Draw(img)

    # ── Bord hairline façon carte gaufrée / pochette (pas une bannière web :
    # un cadre, des coins arrondis, comme la carte de membre #circuit-lock) ──
    frame_inset = 22
    draw.rounded_rectangle(
        [frame_inset, frame_inset, W - frame_inset, H - frame_inset],
        radius=16, outline=HAIRLINE, width=2,
    )

    # ── Numéral géant en filigrane graphite (Fraunces Medium), posé sur le
    # sillon, coin haut droit — même logique que le hero d'issue (numéral
    # graphite avec contour subtil). ──
    numeral = f"Nº{issue_num:02d}"
    f_numeral = _font("Fraunces-Medium.ttf", 230)
    n_bbox = draw.textbbox((0, 0), numeral, font=f_numeral)
    n_w = n_bbox[2] - n_bbox[0]
    n_x = W - margin - n_w - n_bbox[0]
    n_y = -18 - n_bbox[1]
    draw.text((n_x, n_y), numeral, font=f_numeral, fill=GRAPHITE)

    # ── Sceau CF, haut gauche : cercle hairline + « CF » Space Mono Bold,
    # avec le lockup mono « CIRCUIT FERMÉ · SOCIÉTÉ D'ÉCOUTE ». ──
    seal_r = 27
    seal_cx = margin + seal_r
    seal_cy = margin + seal_r
    f_cf = _font("SpaceMono-Bold.ttf", 20)
    _draw_seal(draw, seal_cx, seal_cy, seal_r, f_cf)

    text_x = margin + seal_r * 2 + 20
    f_wordmark = _font("SpaceMono-Bold.ttf", 17)
    f_subtitle = _font("SpaceMono-Regular.ttf", 12)
    wm_text = _tracked("CIRCUIT FERMÉ", " ")
    st_text = _tracked("SOCIÉTÉ D'ÉCOUTE", " ")

    wm_bbox = draw.textbbox((0, 0), wm_text, font=f_wordmark)
    cy = seal_cy - seal_r
    draw.text((text_x, cy - wm_bbox[1]), wm_text, font=f_wordmark, fill=OS)
    cy += (wm_bbox[3] - wm_bbox[1]) + 8

    st_bbox = draw.textbbox((0, 0), st_text, font=f_subtitle)
    draw.text((text_x, cy - st_bbox[1]), st_text, font=f_subtitle, fill=CREUSE)

    # ── Pastille métal + label d'édition, sous le lockup : disque plein du
    # métal de l'édition, comme un pressage coloré, + « ÉDITION Nº12 · OR ». ──
    label_y = margin + seal_r * 2 + 34
    dot_r = 6
    dot_cy = label_y + 7
    draw.ellipse([margin, dot_cy - dot_r, margin + 2 * dot_r, dot_cy + dot_r], fill=metal_color)
    edition_text = _tracked(f"ÉDITION Nº{issue_num:02d} · {metal_name}", " ")
    f_edition = _font("SpaceMono-Regular.ttf", 13)
    ed_bbox = draw.textbbox((0, 0), edition_text, font=f_edition)
    draw.text((margin + 2 * dot_r + 14, dot_cy - (ed_bbox[3] - ed_bbox[1]) / 2 - ed_bbox[1]), edition_text, font=f_edition, fill=BRUME)

    # ── Tagline, Fraunces italique, os, wrap max 3 lignes, réduction auto,
    # centrée verticalement dans la zone libre entre le label et le pied. ──
    tagline = no_dash(content.get("tagline_plain", ""))
    tagline_max_w = W - 2 * margin
    tagline_sizes = [64, 56, 48, 42]
    lines: list[str] = []
    f_tagline = None
    for size in tagline_sizes:
        f_tagline = _font("Fraunces-Italic.ttf", size)
        lines = _wrap(draw, tagline, f_tagline, tagline_max_w, 3)
        consumed = " ".join(lines)
        if len(consumed) >= len(tagline.rstrip()) or size == tagline_sizes[-1]:
            break

    line_bbox = draw.textbbox((0, 0), "Ag", font=f_tagline)
    line_h = int((line_bbox[3] - line_bbox[1]) * 1.22)

    zone_top = label_y + 46
    zone_bottom = H - margin - 54
    block_h = line_h * len(lines)
    block_top = zone_top + max(0, (zone_bottom - zone_top - block_h) // 2)
    y = block_top
    for line in lines:
        draw.text((margin, y - line_bbox[1]), line, font=f_tagline, fill=OS)
        y += line_h

    # ── Ligne mono discrète en pied : date + lecture (+ écoute), en brume,
    # même registre que .hero-meta / .reading-time côté site. ──
    date_str = _row_date(content.get("date_iso", ""))
    reading = no_dash(content.get("reading_time", ""))
    listening = no_dash(content.get("listening_time", ""))
    parts = [p for p in [date_str, f"LECTURE {reading}".upper() if reading else "", f"ÉCOUTE {listening}".upper() if listening else ""] if p]
    footer = "   ·   ".join(parts)
    f_footer = _font("SpaceMono-Regular.ttf", 15)
    fb = draw.textbbox((0, 0), footer, font=f_footer)
    draw.text((margin, H - margin - (fb[3] - fb[1]) - fb[1]), footer, font=f_footer, fill=BRUME)

    return img


def build_card(content: dict) -> Path:
    """Rend et écrit issues/NN/card.png. Retourne le chemin écrit."""
    num = f"{content['issue_num']:02d}"
    out_dir = ISSUES / num
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "card.png"
    img = render_card(content)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, help="Chemin du JSON de contenu")
    parser.add_argument("--out", help="Chemin de sortie (défaut : issues/NN/card.png)")
    args = parser.parse_args()

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    if args.out:
        img = render_card(content)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG", optimize=True)
    else:
        out_path = build_card(content)
    print(f"[OK] Carte de partage -> {out_path}")


if __name__ == "__main__":
    main()
