"""
Registre anti-répétition : liste tout ce qui a déjà été utilisé dans les
numéros publiés (artistes, labels, tracks), à consulter AVANT toute nouvelle
sélection. Source de vérité : les content/NN.json eux-mêmes, rien à maintenir.

  python tools/track_history.py            # registre lisible
  python tools/track_history.py --check "Nom d'artiste ou label"
"""
import argparse
import json
import re
from pathlib import Path

CONTENT = Path(__file__).parent.parent / "content"
SEP = re.compile(r" [·—–] ")


def collect():
    used = {}
    for f in sorted(CONTENT.glob("[0-9][0-9].json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        num = f.stem
        artists, labels, tracks = [], set(), []
        for b in d.get("blocks", []):
            for t in b.get("tracks", []) or []:
                name = t.get("name", "")
                tracks.append(name)
                artist = SEP.split(name, 1)[0].strip()
                if artist and artist not in artists:
                    artists.append(artist)
                if t.get("label"):
                    labels.add(t["label"])
            if b.get("type") == "section" and b.get("paragraphs"):
                # les sections label citent un label dans le heading « Le label · X »
                h = b.get("heading", "")
                m = re.search(r"[Ll]abel\s*[·:]\s*(.+)", h)
                if m:
                    labels.add(m.group(1).strip())
        if d.get("tagline_plain", "").strip():
            used[num] = {"artists": artists, "labels": sorted(labels), "tracks": tracks}
    return used


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", help="Nom à tester (artiste, label ou track)")
    args = p.parse_args()
    used = collect()

    if args.check:
        needle = args.check.lower()
        latest = max((int(n) for n in used), default=0)
        hits = []
        for num, u in used.items():
            for kind in ("artists", "labels", "tracks"):
                for v in u[kind]:
                    if needle in v.lower():
                        gap = latest + 1 - int(num)
                        verdict = "LIBRE (≥10 éditions)" if gap >= 10 else f"BLOQUÉ (écart {gap}, mini 10)"
                        hits.append(f"N°{num} · {kind[:-1]} · {v} → {verdict}")
        if hits:
            print("\n".join(hits))
        else:
            print("OK : jamais utilisé en édition.")
        # Blocklist playlists : Adam connaît déjà ces sons.
        pl = (CONTENT / "playlists")
        if pl.exists():
            for f in pl.glob("*.txt"):
                if re.search(re.escape(args.check), f.read_text(encoding="utf-8"), re.I):
                    print(f"BLOCKLIST : présent dans {f.name} (playlists d'Adam, interdit de suggestion)")
                    break
        return

    for num, u in used.items():
        print(f"\n== N°{num} ==")
        print("  artistes :", " · ".join(u["artists"]))
        print("  labels   :", " · ".join(u["labels"]))
    total_a = {a for u in used.values() for a in u["artists"]}
    total_l = {l for u in used.values() for l in u["labels"]}
    print(f"\nTotal : {sum(len(u['tracks']) for u in used.values())} tracks, "
          f"{len(total_a)} artistes, {len(total_l)} labels utilisés.")


if __name__ == "__main__":
    main()
