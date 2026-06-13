"""
Rend une issue KAPMAN SIGNAL en page web statique à partir d'un JSON de contenu.

  python tools/build_issue.py --content content/10.json

Le JSON décrit l'issue (voir content/SCHEMA.md). La DA est garantie identique
à chaque issue car elle vient du template templates/issue.html.j2 (extrait de N°09).

Étapes :
  1. charge le JSON
  2. rend issues/NN/index.html via Jinja2
  3. met à jour la liste des issues dans index.html (page d'accueil)
"""
import argparse
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.parent
TEMPLATES = ROOT / "templates"
ISSUES = ROOT / "issues"


def render_issue(content: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "j2"]),
    )
    tmpl = env.get_template("issue.html.j2")

    # Compte les sections (pour l'affichage "N / total")
    section_count = sum(1 for b in content["blocks"] if b["type"] == "section")
    # Numérote les sections au fil de l'eau
    idx = 0
    for b in content["blocks"]:
        if b["type"] == "section":
            idx += 1
            b["index"] = idx

    return tmpl.render(section_count=section_count, **content)


def write_issue(content: dict) -> Path:
    num = str(content["issue_num"]).zfill(2)
    out_dir = ISSUES / num
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(render_issue(content), encoding="utf-8")
    return out_file


def update_home(content: dict):
    """Insère/maj la ligne d'issue dans index.html (liste des issues)."""
    home = ROOT / "index.html"
    html = home.read_text(encoding="utf-8")

    num = str(content["issue_num"]).zfill(2)
    title = content["tagline_plain"]
    month = content["month_label"]

    row = (
        f'    <a class="issue-row" href="issues/{num}/">\n'
        f'      <span class="issue-num">N°{num}</span>\n'
        f'      <span class="issue-title">{title}</span>\n'
        f'      <span class="issue-date">{month}</span>\n'
        f'    </a>'
    )

    # Si la ligne pour ce numéro existe déjà, on la remplace ; sinon on l'insère
    # juste après <div class="lbl">Issues</div> (donc en tête de liste = plus récent).
    existing = re.search(
        rf'    <a class="issue-row" href="issues/{num}/">.*?</a>',
        html, re.DOTALL,
    )
    if existing:
        html = html[:existing.start()] + row + html[existing.end():]
    else:
        anchor = '<div class="lbl">Issues</div>'
        pos = html.find(anchor)
        if pos == -1:
            raise RuntimeError("Ancre 'Issues' introuvable dans index.html")
        insert_at = pos + len(anchor)
        html = html[:insert_at] + "\n" + row + html[insert_at:]

    home.write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, help="Chemin du JSON de contenu")
    parser.add_argument("--no-home", action="store_true", help="Ne pas toucher index.html")
    args = parser.parse_args()

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    out = write_issue(content)
    print(f"[OK] Issue rendue -> {out}")

    if not args.no_home:
        update_home(content)
        print(f"[OK] Page d'accueil mise a jour (N{str(content['issue_num']).zfill(2)})")


if __name__ == "__main__":
    main()
