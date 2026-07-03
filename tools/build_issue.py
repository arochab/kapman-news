"""
Rend une issue CIRCUIT FERMÉ en page web statique à partir d'un JSON de contenu.

  python tools/build_issue.py --content content/10.json

Le JSON décrit l'issue (voir content/SCHEMA.md). La DA est garantie identique
à chaque issue car elle vient du template templates/issue.html.j2 (extrait de N°09).

Étapes :
  1. charge le JSON
  2. rend issues/NN/index.html via Jinja2
  3. met à jour la liste des issues dans index.html (page d'accueil)
"""
import argparse
import html
import json
import re
import unicodedata
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.parent
TEMPLATES = ROOT / "templates"
ISSUES = ROOT / "issues"
CONTENT = ROOT / "content"

# Carte de partage (OG) : import optionnel, échec robuste. Un Pillow absent
# ou une police manquante ne doit jamais faire échouer le build de l'issue,
# seulement priver le lien social de sa card.png (le template a un fallback
# meta propre dans ce cas — cf issue.html.j2).
try:
    from og_card import build_card as _build_og_card
except Exception:  # ImportError (Pillow absent) ou toute erreur d'import des polices
    _build_og_card = None

YOUTUBE_ID_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{6,})")


def slugify(text: str) -> str:
    """lower, accents -> ascii, tout non-alnum -> '-', trim les '-' superflus."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _existing_issue_nums() -> list[int]:
    """Liste triée des numéros d'issue déjà rendus (issues/NN/ existants)."""
    nums = []
    if ISSUES.exists():
        for d in ISSUES.iterdir():
            if d.is_dir() and re.fullmatch(r"\d{2}", d.name):
                nums.append(int(d.name))
    return sorted(nums)


def compute_prev_next(issue_num: int):
    """prev = plus grand numéro existant < issue_num, next = plus petit > issue_num."""
    nums = _existing_issue_nums()
    prev_candidates = [n for n in nums if n < issue_num]
    next_candidates = [n for n in nums if n > issue_num]
    prev_num = f"{max(prev_candidates):02d}" if prev_candidates else None
    next_num = f"{min(next_candidates):02d}" if next_candidates else None
    return prev_num, next_num


def load_site() -> dict:
    """Charge content/site.json (config globale non liée à une issue précise :
    membership_url, membership_price, …). Absent -> dict vide (falsy en Jinja,
    donc le bloc membership ne s'affiche simplement pas)."""
    site_path = CONTENT / "site.json"
    if not site_path.exists():
        return {}
    return json.loads(site_path.read_text(encoding="utf-8"))


def extract_listen_all(content: dict):
    """Extrait les IDs YouTube (ordre, dédupliqués) de tous les tracks[].links[].url."""
    ids = []
    seen = set()
    for b in content.get("blocks", []):
        for t in b.get("tracks", []) or []:
            for link in t.get("links", []) or []:
                url = link.get("url", "")
                m = YOUTUBE_ID_RE.search(url)
                if m:
                    vid = m.group(1)
                    if vid not in seen:
                        seen.add(vid)
                        ids.append(vid)
    listen_count = len(ids)
    listen_all_url = None
    if listen_count >= 2:
        listen_all_url = "https://www.youtube.com/watch_videos?video_ids=" + ",".join(ids)
    return listen_all_url, listen_count


def render_issue(content: dict, og_image_available: bool = False) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "j2"]),
    )
    tmpl = env.get_template("issue.html.j2")

    # Compte les sections (pour l'affichage "N / total")
    section_count = sum(1 for b in content["blocks"] if b["type"] == "section")
    # Numérote les sections au fil de l'eau + slug par track
    idx = 0
    for b in content["blocks"]:
        if b["type"] == "section":
            idx += 1
            b["index"] = idx
        for t in b.get("tracks", []) or []:
            t["slug"] = slugify(t["name"])

    prev_num, next_num = compute_prev_next(content["issue_num"])
    listen_all_url, listen_count = extract_listen_all(content)
    site = load_site()

    # circuit (contenu membre chiffre, optionnel) : passe explicitement comme
    # site, et retire du dict spread ci-dessous pour eviter un doublon de
    # kwarg. Absent (anciennes issues) -> None -> falsy en Jinja, rendu
    # strictement identique a aujourd'hui.
    circuit = content.get("circuit")
    content_rest = {k: v for k, v in content.items() if k != "circuit"}

    return tmpl.render(
        section_count=section_count,
        prev_num=prev_num,
        next_num=next_num,
        listen_all_url=listen_all_url,
        listen_count=listen_count,
        site=site,
        circuit=circuit,
        og_image_available=og_image_available,
        **content_rest,
    )


def write_issue(content: dict) -> Path:
    num = str(content["issue_num"]).zfill(2)
    out_dir = ISSUES / num
    out_dir.mkdir(parents=True, exist_ok=True)
    # La carte de partage est générée AVANT le rendu HTML : le template a
    # besoin de savoir si issues/NN/card.png existe pour émettre (ou non)
    # les balises og:image / twitter:image sans jamais pointer un lien mort.
    og_image_available = build_og_card(content)
    out_file = out_dir / "index.html"
    out_file.write_text(render_issue(content, og_image_available=og_image_available), encoding="utf-8")
    return out_file


def build_og_card(content: dict) -> bool:
    """Génère issues/NN/card.png (image de partage OG). Best effort : toute
    erreur (Pillow absent, police manquante, JSON incomplet) n'interrompt
    jamais le build de l'issue, juste un warning sur stderr. Retourne True
    si la carte a bien été écrite (utilisé par le template pour les meta OG)."""
    if _build_og_card is None:
        print("[WARN] Pillow indisponible : carte de partage (card.png) non générée.")
        return False
    try:
        out = _build_og_card(content)
        print(f"[OK] Carte de partage -> {out}")
        return True
    except Exception as exc:  # noqa: BLE001 — best effort, ne doit jamais casser le build
        print(f"[WARN] Échec génération carte de partage : {exc}")
        return False


def _row_piece_count(content: dict) -> int:
    """Nombre de pièces du registre pour la ligne d'archive home.

    Priorité à `circuit.total` (posé par `tools/circuit.py --seal` sur les
    numéros fermés freemium : compte les pièces publiques + scellées).
    Rétrocompat : sans ce champ (numéros non fermés), on compte simplement
    les tracks des blocs `section`."""
    circuit = content.get("circuit") or {}
    if circuit.get("total"):
        return int(circuit["total"])
    total = 0
    for b in content.get("blocks", []):
        if b.get("type") != "section":
            continue
        total += len(b.get("tracks") or [])
    return total


def _row_date(date_iso: str) -> str:
    """date_iso 'YYYY-MM-DD' -> 'JJ.MM.AA'."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", date_iso or "")
    if not m:
        return date_iso or ""
    yyyy, mm, dd = m.groups()
    return f"{dd}.{mm}.{yyyy[2:]}"


def build_row_html(content: dict) -> str:
    """Rangée du registre home v5 : index 3 chiffres, tagline, nb de pièces, date.
    Cf CLAUDE.md § Design system + docs/CHARTE-V5 « Index de sélection »."""
    num = str(content["issue_num"]).zfill(3)
    title = html.escape(content.get("tagline_plain", ""))
    date = html.escape(_row_date(content.get("date_iso", "")))
    count = _row_piece_count(content)
    count_label = html.escape(f"{count} pièce" + ("" if count == 1 else "s"))
    href_num = str(content["issue_num"]).zfill(2)

    return (
        f'    <a class="registry-row" href="issues/{href_num}/">\n'
        f'      <span class="registry-idx tnum">{num}</span>\n'
        f'      <span class="registry-main">\n'
        f'        <span class="tagline">{title}</span>\n'
        f'        <span class="meta tnum">{date}</span>\n'
        f'      </span>\n'
        f'      <span class="registry-count tnum">{count_label}</span>\n'
        f'    </a>'
    )


# Détecte une row existante (ancien format issue-row OU nouveau format registry-row) pour ce numéro.
def _row_pattern(num: str) -> re.Pattern:
    return re.compile(
        rf'    <a class="(?:issue-row|registry-row)[^"]*" href="issues/{num}/">.*?</a>',
        re.DOTALL,
    )


def update_home(content: dict):
    """Insère/maj la ligne d'issue dans index.html (liste des issues)."""
    home = ROOT / "index.html"
    html_src = home.read_text(encoding="utf-8")

    num = str(content["issue_num"]).zfill(2)
    row = build_row_html(content)

    # Si la ligne pour ce numéro existe déjà (ancien OU nouveau format), on la
    # remplace ; sinon on l'insère juste après l'ancre "Archive" (= en tête de
    # liste, la plus récente en premier).
    existing = _row_pattern(num).search(html_src)
    if existing:
        html_src = html_src[:existing.start()] + row + html_src[existing.end():]
    else:
        anchor = 'id="archive-lbl"'
        pos = html_src.find(anchor)
        if pos == -1:
            raise RuntimeError("Ancre 'archive-lbl' introuvable dans index.html")
        # Insère après le </div> du label (pas après le > de la balise ouvrante,
        # qui couperait le div en deux).
        insert_at = html_src.find("</div>", pos) + len("</div>")
        html_src = html_src[:insert_at] + "\n" + row + html_src[insert_at:]

    # Recompte les rows et remet à jour le libellé "Archive · N numéros".
    row_count = len(re.findall(r'class="registry-row"', html_src))
    html_src = re.sub(
        r'(<div class="section-divider" id="archive-lbl">Archive [·—] )\d+( numéros?</div>)',
        lambda m: f"{m.group(1)}{row_count}{m.group(2)}",
        html_src,
    )

    home.write_text(html_src, encoding="utf-8")


def rebuild_all():
    """Re-rend chaque content/NN.json pour lequel issues/NN/index.html existe déjà.

    Protège le squelette vide (ex. content/11.json tant qu'issues/11/ n'existe
    pas) : on ne rend jamais un numéro qui n'a pas déjà été publié.
    """
    existing_nums = set(_existing_issue_nums())
    content_files = sorted(
        CONTENT.glob("[0-9][0-9].json"),
        key=lambda p: int(p.stem),
    )
    for path in content_files:
        num = int(path.stem)
        if num not in existing_nums:
            continue
        content = json.loads(path.read_text(encoding="utf-8"))
        out = write_issue(content)
        update_home(content)
        print(f"[OK] Rebuild N°{num:02d} -> {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", help="Chemin du JSON de contenu")
    parser.add_argument("--no-home", action="store_true", help="Ne pas toucher index.html")
    parser.add_argument(
        "--rebuild-all", action="store_true",
        help="Re-rend tous les content/NN.json déjà publiés (issues/NN/ existant), ordre croissant.",
    )
    args = parser.parse_args()

    if args.rebuild_all:
        rebuild_all()
        return

    if not args.content:
        parser.error("--content est requis (sauf avec --rebuild-all)")

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    out = write_issue(content)
    print(f"[OK] Issue rendue -> {out}")

    if not args.no_home:
        update_home(content)
        print(f"[OK] Page d'accueil mise a jour (N{str(content['issue_num']).zfill(2)})")


if __name__ == "__main__":
    main()
