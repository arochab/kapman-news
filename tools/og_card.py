"""
Génère la carte de partage (Open Graph, 1200x630) d'une issue CIRCUIT FERMÉ.

  python tools/og_card.py --content content/10.json

Rendu direct avec Pillow (pas de navigateur headless) à partir des mêmes
polices que le site (Hanken Grotesk, IBM Plex Mono, committées localement
dans tools/assets/fonts/ · aucun téléchargement au build CI) et des mêmes
couleurs de marque que templates/issue.html.j2.

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

# ── Couleurs de marque (identiques à templates/issue.html.j2 :root) ──
INK = (14, 15, 20)
CREAM = (240, 238, 230)
RED = (232, 58, 46)
GREEN = (31, 200, 94)
BLUE = (58, 108, 240)
META = (138, 141, 153)  # --meta

# accent par issue_num % 3 · même correspondance que templates/issue.html.j2
# ({%- set acc = ['red', 'green', 'blue'][issue_num % 3] -%}) et build_issue.py
# (build_row_html : accent_idx = issue_num % 3).
ACCENTS = [RED, GREEN, BLUE]

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


def _signal_glyph_width(scale: float) -> int:
    bar_w = round(6 * scale)
    gap = round(5 * scale)
    return 3 * bar_w + 2 * gap


def _draw_signal_glyph(draw: ImageDraw.ImageDraw, x: int, y_baseline: int, scale: float = 2.6):
    """3 barres arrondies R/V/B, hauteurs relatives 12/22/17 (signature graphique),
    ancrées sur y_baseline (bas des barres), largeur ~6px * scale."""
    bar_w = round(6 * scale)
    gap = round(5 * scale)
    radius = bar_w // 2
    heights = [round(12 * scale), round(22 * scale), round(17 * scale)]
    colors = [RED, GREEN, BLUE]
    cx = x
    for h, color in zip(heights, colors):
        y0 = y_baseline - h
        draw.rounded_rectangle([cx, y0, cx + bar_w, y_baseline], radius=radius, fill=color)
        cx += bar_w + gap
    return cx - gap  # x de fin (bord droit de la dernière barre)


def _tracked(text: str, spacing: str = " ") -> str:
    """Simule le letter-spacing large de la version web pour un rendu mono."""
    return spacing.join(text)


def _blend(base: tuple, over: tuple, alpha: float) -> tuple:
    """Mélange 'over' sur 'base' à l'opacité alpha (0..1), en RGB opaque
    (équivalent d'un alpha-compositing pré-calculé, pas besoin de canal
    alpha réel puisque le fond sous le numéral est un ink plat uniforme)."""
    return tuple(round(b + (o - b) * alpha) for b, o in zip(base, over))


def render_card(content: dict) -> Image.Image:
    issue_num = content["issue_num"]
    accent = ACCENTS[issue_num % 3]

    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)

    margin = 64

    # ── Numéral géant en filigrane, teinté accent, contour seul (comme le
    # hero web : -webkit-text-stroke + opacity .35) — texture de fond, la
    # tagline se pose par dessus. Dessiné AVANT la triple rule et le lockup
    # pour qu'ils restent nets par dessus. Fond ink plat -> pas besoin d'un
    # vrai canal alpha, l'opacité est pré-mélangée (_blend). ──
    numeral = f"N°{issue_num:02d}"
    f_numeral = _font("HankenGrotesk-ExtraBold.ttf", 250)
    n_bbox = draw.textbbox((0, 0), numeral, font=f_numeral, stroke_width=3)
    n_w = n_bbox[2] - n_bbox[0]
    n_x = W - margin - n_w - n_bbox[0]
    n_y = 34 - n_bbox[1]
    stroke_color = _blend(INK, accent, 0.42)
    draw.text(
        (n_x, n_y), numeral, font=f_numeral,
        fill=INK, stroke_width=3, stroke_fill=stroke_color,
    )

    # ── Triple rule pleine largeur, en tête ET en pied (les pages du site
    # sont toujours bookendées par les deux rules · même signature ici) ──
    rule_h = 7
    third = W / 3
    for y0, y1 in [(0, rule_h), (H - rule_h, H)]:
        draw.rectangle([0, y0, third, y1], fill=RED)
        draw.rectangle([third, y0, 2 * third, y1], fill=GREEN)
        draw.rectangle([2 * third, y0, W, y1], fill=BLUE)

    # ── Lockup logo (haut gauche) : glyphe signal + CIRCUIT / FERMÉ ──
    # Empile CIRCUIT (Hanken ExtraBold) au dessus de FERMÉ (Plex Mono tracké),
    # chaque ligne posée par son bbox d'encre réel (évite tout chevauchement
    # dû aux marges internes variables des polices).
    glyph_scale = 2.8
    text_x = margin + _signal_glyph_width(glyph_scale) + 20
    f_wordmark = _font("HankenGrotesk-ExtraBold.ttf", 34)
    f_signal = _font("IBMPlexMono-Medium.ttf", 14)
    line_gap = 10

    cy = margin
    wm_bbox = draw.textbbox((0, 0), "CIRCUIT", font=f_wordmark)
    draw.text((text_x, cy - wm_bbox[1]), "CIRCUIT", font=f_wordmark, fill=CREAM)
    cy += (wm_bbox[3] - wm_bbox[1]) + line_gap

    sig_text = _tracked("FERMÉ", " ")
    sig_bbox = draw.textbbox((0, 0), sig_text, font=f_signal)
    draw.text((text_x, cy - sig_bbox[1]), sig_text, font=f_signal, fill=META)
    cy += (sig_bbox[3] - sig_bbox[1])

    glyph_baseline = cy
    _draw_signal_glyph(draw, margin, glyph_baseline, scale=glyph_scale)

    # ── Tagline, grande, cream, wrap max 3 lignes, centrée verticalement
    # dans la zone libre entre le logo et la ligne mono du bas. ExtraBold :
    # même graisse que le <h1> du hero (Hanken 800), la carte parle la même
    # voix que la page qu'elle annonce. ──
    tagline = no_dash(content.get("tagline_plain", ""))
    tagline_max_w = W - 2 * margin
    f_tagline = _font("HankenGrotesk-ExtraBold.ttf", 64)
    lines = _wrap(draw, tagline, f_tagline, tagline_max_w, 3)
    if len(lines) > 2:
        f_tagline = _font("HankenGrotesk-ExtraBold.ttf", 52)
        lines = _wrap(draw, tagline, f_tagline, tagline_max_w, 3)

    line_bbox = draw.textbbox((0, 0), "Ag", font=f_tagline)
    line_h = int((line_bbox[3] - line_bbox[1]) * 1.3)
    # Barre d'accent courte au-dessus de la tagline (langage .s-accent du
    # site) : ancre le bloc et pose l'accent d'issue dans la composition.
    bar_h, bar_gap = 5, 26
    block_h = bar_h + bar_gap + line_h * len(lines)

    zone_top = margin + 140       # sous le lockup
    zone_bottom = H - margin - 56  # au dessus de la ligne mono du bas
    block_top = zone_top + max(0, (zone_bottom - zone_top - block_h) // 2)
    draw.rectangle([margin, block_top, margin + 56, block_top + bar_h], fill=accent)
    y = block_top + bar_h + bar_gap
    for line in lines:
        draw.text((margin, y), line, font=f_tagline, fill=CREAM)
        y += line_h

    # ── Ligne mono discrète en bas : date + lecture (+ écoute), majuscules
    # comme tous les registres mono du site (.hero-meta, .reading-time) ──
    date_str = _row_date(content.get("date_iso", ""))
    reading = no_dash(content.get("reading_time", ""))
    listening = no_dash(content.get("listening_time", ""))
    parts = [p for p in [date_str, f"lecture {reading}" if reading else "", f"écoute {listening}" if listening else ""] if p]
    footer = "   ·   ".join(parts).upper()
    f_footer = _font("IBMPlexMono-Regular.ttf", 16)
    draw.text((margin, H - margin), footer, font=f_footer, fill=META)

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
