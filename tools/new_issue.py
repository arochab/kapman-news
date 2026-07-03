"""
Orchestrateur d'une nouvelle issue CIRCUIT FERMÉ.

  python tools/new_issue.py --num 10

Ce script structure le workflow ; l'écriture éditoriale du contenu (tracks,
textes) reste pilotée par Claude en session, dans le respect des règles :
  - aucune répétition (cf memory/newsletter_track_history.md)
  - liens YouTube réels uniquement (playlists CSV)

Étapes :
  1. Vérifie qu'un content/NN.json existe (sinon, en crée un squelette à remplir).
  2. (optionnel) lance la recherche de releases via le research.py existant.
  3. Rend la page via build_issue.py (met à jour la home).
  4. Rappelle les étapes manuelles : maj mémoire + git push (déclenche la notif).

Le research.py vit dans NEWSLETTER DEMO/ — on le réutilise tel quel s'il est dispo.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
DEMO = ROOT.parent / "NEWSLETTER DEMO"   # pipeline WAT existant
RESEARCH = DEMO / "tools" / "research.py"
MEMORY = DEMO / "memory" / "newsletter_track_history.md"

SKELETON = {
    "issue_num": None,
    "date_iso": "YYYY-MM-DD",
    "month_label": "Mois AAAA",
    "reading_time": "4 min",
    "playlist_url": "",
    "listening_time": "",
    "tagline_plain": "",
    "tagline_html": "",
    "summary_bullets": ["", "", "", ""],
    "blocks": [
        {"type": "section", "accent": "red", "heading": "", "tracks": []},
        {"type": "stat", "accent": "green", "number": "", "context": ""},
        {"type": "section", "accent": "green", "heading": "", "tracks": []},
        {"type": "stat", "accent": "blue", "number": "", "context": ""},
        {"type": "section", "accent": "blue", "heading": "", "paragraphs": [""]},
        {"type": "section", "accent": "red", "heading": "Note de studio", "paragraphs": [""]},
    ],
    "forward_text": "",
}


def ensure_content(num: int) -> Path:
    path = CONTENT / f"{num:02d}.json"
    if path.exists():
        print(f"[OK] content/{num:02d}.json existe deja.")
        return path
    CONTENT.mkdir(parents=True, exist_ok=True)
    skel = dict(SKELETON)
    skel["issue_num"] = num
    path.write_text(json.dumps(skel, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[NEW] Squelette cree -> content/{num:02d}.json")
    print("      Remplis-le (Claude en session) avant de relancer avec --build.")
    return path


def run_research(topic: str):
    if not RESEARCH.exists():
        print(f"[WARN] research.py introuvable ({RESEARCH}) - etape sautee.")
        return
    print(f"[..] Recherche : {topic}")
    subprocess.run([sys.executable, str(RESEARCH), "--topic", topic, "--num-sources", "5"],
                   check=False)


def build(num: int):
    path = CONTENT / f"{num:02d}.json"
    if not path.exists():
        print(f"[ERR] content/{num:02d}.json manquant. Lance d'abord sans --build.")
        sys.exit(1)
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_issue.py"),
                    "--content", str(path)], check=True)


def reminders(num: int):
    print("\n--- Etapes manuelles restantes ---")
    print(f"1. Verifier le rendu : issues/{num:02d}/index.html")
    print(f"2. Mettre a jour la memoire : {MEMORY}")
    print("   (ajouter tracks/artistes/labels de cette issue)")
    print("3. git add -A && git commit -m \"CIRCUIT FERMÉ N°{:02d}\" && git push".format(num))
    print("   -> GitHub Actions envoie la notif push automatiquement.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, required=True, help="Numero d'issue")
    parser.add_argument("--research", metavar="TOPIC", help="Lance la recherche de releases")
    parser.add_argument("--build", action="store_true", help="Rend la page depuis le JSON")
    args = parser.parse_args()

    if args.research:
        run_research(args.research)

    if args.build:
        build(args.num)
        reminders(args.num)
    else:
        ensure_content(args.num)


if __name__ == "__main__":
    main()
