"""
Génère la carte de partage (Open Graph, 1200x630) d'une issue CIRCUIT FERMÉ.

  python tools/og_card.py --content content/11.json

Rendu direct avec Pillow (pas de navigateur headless) à partir des mêmes
polices que le site (Inter Tight, B612 Mono, committées localement dans
tools/assets/fonts/ · aucun téléchargement au build CI) et des mêmes
couleurs de marque que templates/issue.html.j2 (charte v5, « Index de
sélection »).

Composition : la fiche d'un registre, pas une bannière web. Fond ivoire,
cadre noir 2px doublé d'un filet fin extérieur, « ÉD. 011 » géant en B612
Mono gris structure posé en fond de registre, wordmark + kicker en tête,
tagline Inter Tight ExtraBold alignée à droite, deux ou trois barres de
caviardage noires en bas à droite (l'intrigue dans WhatsApp), pied B612
gris (date · pièces · lecture). Si le numéro est fermé (champ `circuit`),
petit tampon « RÉSERVÉ » à bordure rouge double, posé droit.

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

# ── Couleurs de marque (identiques au :root v5 de templates/issue.html.j2) ──
IVOIRE = (252, 251, 247)     # #FCFBF7 · fond
NOIR = (18, 18, 18)          # #121212 · encre
STRUCTURE = (200, 197, 188)  # #C8C5BC · filets, numéral de fond
GRIS = (111, 108, 100)       # #6F6C64 · texte secondaire
ROUGE = (215, 38, 30)        # #D7261E · strate membre uniquement (tampon)

DASH_RE = re.compile(r"\s*[—–]\s*")


def no_dash(text: str) -> str:
    """Aucun tiret cadratin ou demi cadratin dans un texte rendu : remplacé
    par ' · ' (règle éditoriale)."""
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


def _piece_count(content: dict) -> int:
    """Nombre total de pièces du numéro : tracks publiques des blocs +
    pièces scellées (circuit.total prime, sinon circuit.pieces)."""
    count = 0
    for block in content.get("blocks", []) or []:
        count += len(block.get("tracks", []) or [])
    circuit = content.get("circuit")
    if isinstance(circuit, dict):
        total = circuit.get("total")
        if isinstance(total, int) and total > 0:
            return total
        pieces = circuit.get("pieces")
        if isinstance(pieces, list):
            count += len(pieces)
    return count


def _draw_cartouche_cf(draw: ImageDraw.ImageDraw, right: int, top: int) -> None:
    """Micro-signe : « CF » Inter Tight ExtraBold ivoire dans un rectangle
    noir plein, comme un cartouche de registre (jamais de cercle)."""
    f_cf = _font("InterTight-ExtraBold.ttf", 24)
    bbox = draw.textbbox((0, 0), "CF", font=f_cf)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 14, 9
    bw, bh = tw + 2 * pad_x, th + 2 * pad_y
    x0 = right - bw
    draw.rectangle([x0, top, right, top + bh], fill=NOIR)
    draw.text((x0 + pad_x - bbox[0], top + pad_y - bbox[1]), "CF", font=f_cf, fill=IVOIRE)


def _draw_stamp(img: Image.Image, right: int, top: int) -> None:
    """Tampon « RÉSERVÉ » : bordure rouge double 1px, B612 Mono 700, posé
    droit, léger décalage d'encrage toléré (opacité 0.9), jamais incliné."""
    f_stamp = _font("B612Mono-Bold.ttf", 17)
    text = _tracked("RÉSERVÉ", " ")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bbox = draw.textbbox((0, 0), text, font=f_stamp)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 16, 10
    bw, bh = tw + 2 * pad_x, th + 2 * pad_y
    x0 = right - bw
    ink = ROUGE + (230,)
    draw.rectangle([x0, top, x0 + bw, top + bh], outline=ink, width=1)
    draw.rectangle([x0 + 4, top + 4, x0 + bw - 4, top + bh - 4], outline=ink, width=1)
    draw.text((x0 + pad_x - bbox[0], top + pad_y - bbox[1]), text, font=f_stamp, fill=ink)
    img.paste(overlay, (0, 0), overlay)


def render_card(content: dict) -> Image.Image:
    issue_num = content["issue_num"]

    img = Image.new("RGB", (W, H), IVOIRE)
    draw = ImageDraw.Draw(img)

    margin = 64

    # ── Fond de registre : « ÉD. 011 » géant en B612 Mono Bold gris
    # structure, ancré en bas à gauche. C'est une donnée d'index posée en
    # fond, pas un filigrane fantaisie : dessiné avant tout le reste. ──
    seg_a, seg_b = "ÉD.", f"{issue_num:03d}"
    target_w = 720
    size = 200
    while size > 40:
        f_num = _font("B612Mono-Bold.ttf", size)
        a_bbox = draw.textbbox((0, 0), seg_a, font=f_num)
        b_bbox = draw.textbbox((0, 0), seg_b, font=f_num)
        gap = int(size * 0.24)
        total = (a_bbox[2] - a_bbox[0]) + gap + (b_bbox[2] - b_bbox[0])
        if total <= target_w:
            break
        size -= 8
    n_bottom = H - 66
    x = 56
    draw.text((x - a_bbox[0], n_bottom - a_bbox[3]), seg_a, font=f_num, fill=STRUCTURE)
    x += (a_bbox[2] - a_bbox[0]) + gap
    draw.text((x - b_bbox[0], n_bottom - b_bbox[3]), seg_b, font=f_num, fill=STRUCTURE)

    # ── Cadre : filet fin extérieur + cadre noir 2px (la fiche du registre) ──
    draw.rectangle([10, 10, W - 11, H - 11], outline=STRUCTURE, width=1)
    draw.rectangle([22, 22, W - 23, H - 23], outline=NOIR, width=2)

    # ── Tête : wordmark Inter Tight ExtraBold + kicker B612 Mono gris ──
    f_word = _font("InterTight-ExtraBold.ttf", 32)
    w_bbox = draw.textbbox((0, 0), "CIRCUIT FERMÉ", font=f_word)
    top = 58
    draw.text((margin - w_bbox[0], top - w_bbox[1]), "CIRCUIT FERMÉ", font=f_word, fill=NOIR)

    kicker = "REGISTRE DES SÉLECTIONS · PARIS"
    f_kicker = _font("B612Mono-Regular.ttf", 15)
    k_bbox = draw.textbbox((0, 0), kicker, font=f_kicker)
    k_y = top + (w_bbox[3] - w_bbox[1]) + 16
    draw.text((margin - k_bbox[0], k_y - k_bbox[1]), kicker, font=f_kicker, fill=GRIS)

    # ── Micro-signe CF en haut à droite ; tampon RÉSERVÉ à sa gauche si le
    # numéro est fermé (seul rouge autorisé sur la carte). ──
    _draw_cartouche_cf(draw, right=W - margin, top=top)
    if content.get("circuit"):
        _draw_stamp(img, right=W - margin - 90, top=top)
        draw = ImageDraw.Draw(img)

    # ── Pied B612 gris, aligné à droite : date · N pièces · lecture ──
    date_str = _row_date(content.get("date_iso", ""))
    n_pieces = _piece_count(content)
    reading = no_dash(content.get("reading_time", "") or "")
    parts = [date_str]
    if n_pieces:
        parts.append(f"{n_pieces} PIÈCES" if n_pieces > 1 else "1 PIÈCE")
    if reading:
        parts.append(f"LECTURE {reading}".upper())
    footer = " · ".join(p for p in parts if p)
    f_footer = _font("B612Mono-Regular.ttf", 15)
    fb = draw.textbbox((0, 0), footer, font=f_footer)
    foot_h = fb[3] - fb[1]
    foot_top = H - 60 - foot_h
    draw.text((W - margin - (fb[2] - fb[0]) - fb[0], foot_top - fb[1]), footer, font=f_footer, fill=GRIS)

    # ── Barres de caviardage : 3 barres noires pleines, largeurs variées
    # (stables par numéro), empilées au dessus du pied, alignées à droite.
    # Discrètes : c'est un motif du registre, pas un slogan. ──
    bar_h = 10
    bar_gap = 13
    base = (340, 205, 275)
    bar_widths = [b + ((issue_num * 37 + i * 61) % 70) - 35 for i, b in enumerate(base)]
    bars_bottom = foot_top - 30
    y = bars_bottom
    for bw in bar_widths:
        draw.rectangle([W - margin - bw, y - bar_h, W - margin, y], fill=NOIR)
        y -= bar_h + bar_gap
    bars_top = y + bar_gap

    # ── Tagline Inter Tight ExtraBold noir, alignée à droite au dessus des
    # barres, wrap max 3 lignes avec réduction auto. ──
    tagline = no_dash(content.get("tagline_plain", ""))
    tagline_max_w = 660
    lines: list[str] = []
    f_tagline = None
    for size in (58, 50, 44, 38):
        f_tagline = _font("InterTight-ExtraBold.ttf", size)
        lines = _wrap(draw, tagline, f_tagline, tagline_max_w, 3)
        consumed = " ".join(lines)
        if len(consumed) >= len(tagline.rstrip()) or size == 38:
            break

    line_bbox = draw.textbbox((0, 0), "Agé", font=f_tagline)
    line_h = int((line_bbox[3] - line_bbox[1]) * 1.16)
    block_bottom = bars_top - 34
    y = block_bottom - line_h * len(lines)
    for line in lines:
        lw = draw.textlength(line, font=f_tagline)
        draw.text((W - margin - lw, y - line_bbox[1]), line, font=f_tagline, fill=NOIR)
        y += line_h

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
