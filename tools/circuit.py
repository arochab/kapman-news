"""
Scelle et ouvre le contenu chiffré "circuit fermé" (membres) d'une issue.

  python tools/circuit.py --seal 12 --code "acide-brume-jade-12"
  python tools/circuit.py --check 12 --code "acide-brume-jade-12"
  python tools/circuit.py --open 12 --code "acide-brume-jade-12"
  python tools/circuit.py --gen-code

Le clair membre vit dans content/circuit/NN.json (gitignoré, n'existe qu'en
session d'écriture, jamais commité). --seal rend chaque bloc en HTML via
templates/circuit_fragment.html.j2, assemble le clair, le chiffre en
AES-256-GCM avec une clé dérivée du code (PBKDF2-HMAC-SHA256, 310000
itérations, compatible WebCrypto côté navigateur) et écrit le résultat dans
le champ "circuit" de content/NN.json. --open fait l'inverse : déchiffre et
recrée content/circuit/NN.json à partir du clair.

Contrat détaillé (structure du clair, du champ "circuit", procédure) :
content/SCHEMA.md, section "Numéro à circuit fermé".
"""
import argparse
import base64
import copy
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
CIRCUIT_DIR = CONTENT / "circuit"
TEMPLATES = ROOT / "templates"

# tools/ est déjà sur sys.path quand ce script est lancé directement
# (python tools/circuit.py) ; on le force ici pour couvrir aussi le cas
# import depuis un autre répertoire de travail.
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

PBKDF2_ITERATIONS = 310_000
KEY_LEN = 32
SALT_LEN = 16
IV_LEN = 12

# Liste interne pour --gen-code : mots français courants, sans accent (le code
# doit rester facile à taper), thème matière/signal cohérent avec la marque.
WORDLIST = [
    "acide", "aimant", "ambre", "angle", "arche", "argent", "aube", "axe",
    "base", "bloc", "boue", "bronze", "brume", "cable", "cadence", "chrome",
    "cible", "circuit", "code", "cuivre", "delta", "digue", "disque", "drone",
    "echo", "ecran", "eclipse", "encre", "epave", "fer", "filtre", "flux",
    "forge", "fusion", "givre", "glace", "grain", "grille", "groove", "houle",
    "impulse", "indigo", "jade", "jetee", "kick", "laser", "lame", "lave",
    "ligne", "lueur", "lune", "marge", "matrice", "mecha", "metal", "mine",
    "mode", "mono", "motif", "neon", "nerf", "noyau", "obscur", "onde",
    "orbite", "phase", "pixel", "plasma", "pluie", "pouls", "presse", "pulse",
    "quartz", "radar", "reseau", "riff", "ruban", "sable", "satin", "sceau",
    "signal", "silex", "sillon", "source", "spectre", "stereo", "tempo",
    "texture", "trace", "transit", "tunnel", "vague", "vapeur", "vitre",
    "volt", "zenith", "zinc",
]


def _crypto():
    """Importe les primitives cryptography, message clair si absent (pip
    install cryptography). La CI ne chiffre jamais : cette dépendance n'est
    utile qu'en session d'écriture, jamais dans le pipeline de publication."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
    except ImportError:
        print(
            "[ERR] Le module 'cryptography' est requis (pip install cryptography). "
            "Necessaire uniquement pour sceller/ouvrir un circuit ferme en session, "
            "jamais en CI.",
            file=sys.stderr,
        )
        sys.exit(1)
    return AESGCM, PBKDF2HMAC, hashes


def normalize_code(code: str) -> str:
    """Normalisation du code membre : strip + lowercase, rien d'autre."""
    return code.strip().lower()


def derive_key(code: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256(code normalise, salt, 310000 iterations, 32 octets).

    Compatible WebCrypto.subtle.deriveKey/deriveBits cote navigateur : meme
    algorithme, memes parametres."""
    _, PBKDF2HMAC, hashes = _crypto()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(normalize_code(code).encode("utf-8"))


def encrypt(plaintext: bytes, code: str):
    """AES-256-GCM, IV 12 octets aleatoire, tag concatene en fin de
    ciphertext (comportement par defaut de AESGCM et de WebCrypto).
    Retourne (salt, iv, ciphertext_avec_tag)."""
    AESGCM, _, _ = _crypto()
    salt = secrets.token_bytes(SALT_LEN)
    iv = secrets.token_bytes(IV_LEN)
    key = derive_key(code, salt)
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    return salt, iv, ct


def decrypt(salt: bytes, iv: bytes, ct: bytes, code: str) -> bytes:
    AESGCM, _, _ = _crypto()
    key = derive_key(code, salt)
    return AESGCM(key).decrypt(iv, ct, None)


def _jinja_env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "j2"]),
    )


def render_block(env, block: dict) -> str:
    """Rend un bloc membre en fragment HTML autonome via
    templates/circuit_fragment.html.j2.

    Le bloc suit la meme structure qu'un bloc public (section avec tracks
    ou paragraphs, ou stat ; cf content/SCHEMA.md), plus un champ entier
    "position" (consomme par --seal, pas transmis au template). Les tracks
    recoivent un slug avec la meme convention que build_issue.render_issue,
    pour permettre des ancres dans le fragment.

    Variables passees au template : "block" (le bloc lui meme) et
    "accent_class" (raccourci = block["accent"], ex. "red" ; le template
    choisit comment le prefixer, ex. tracks-{{ accent_class }}, comme le
    fait deja templates/issue.html.j2 pour les blocs publics).
    """
    import build_issue as _build_issue

    for t in block.get("tracks", []) or []:
        t["slug"] = _build_issue.slugify(t["name"])
    accent_class = block.get("accent")
    tmpl = env.get_template("circuit_fragment.html.j2")
    return tmpl.render(block=block, accent_class=accent_class)


def _content_path(num: int) -> Path:
    return CONTENT / f"{num:02d}.json"


def _circuit_clear_path(num: int) -> Path:
    return CIRCUIT_DIR / f"{num:02d}.json"


def cmd_seal(num: int, code: str, kid: str = None, teaser: str = None):
    """Lit content/circuit/NN.json (clair), rend chaque bloc en HTML,
    construit le plaintext {"fragments": [...], "source": {...}}, chiffre,
    et ecrit le champ "circuit" dans content/NN.json (reste du JSON
    preserve, indent 2, ensure_ascii False)."""
    content_path = _content_path(num)
    clear_path = _circuit_clear_path(num)

    if not content_path.exists():
        print(f"[ERR] content/{num:02d}.json introuvable.", file=sys.stderr)
        sys.exit(1)
    if not clear_path.exists():
        print(
            f"[ERR] content/circuit/{num:02d}.json introuvable "
            "(ecrire le clair membre d'abord).",
            file=sys.stderr,
        )
        sys.exit(1)

    content = json.loads(content_path.read_text(encoding="utf-8"))
    clear = json.loads(clear_path.read_text(encoding="utf-8"))
    blocks = clear.get("blocks") or []
    if not blocks:
        print(
            f"[ERR] content/circuit/{num:02d}.json ne contient aucun bloc "
            "('blocks' vide ou absent).",
            file=sys.stderr,
        )
        sys.exit(1)

    env = _jinja_env()
    fragments = []
    count = 0
    for block in blocks:
        position = block.get("position")
        if not isinstance(position, int):
            print(
                f"[ERR] bloc sans 'position' entiere : "
                f"{block.get('heading', '(sans titre)')!r}",
                file=sys.stderr,
            )
            sys.exit(1)
        # render_block ajoute un slug par track (comme build_issue.render_issue) :
        # on rend une copie profonde pour ne jamais muter "clear", qui est
        # sauvegarde tel quel dans le plaintext (champ "source", cf --open).
        html_fragment = render_block(env, copy.deepcopy(block))
        fragments.append({"position": position, "html": html_fragment})
        count += len(block.get("tracks", []) or [])

    if kid is None:
        date_iso = content.get("date_iso", "")
        kid = date_iso[:7] if len(date_iso) >= 7 else ""

    if teaser is None:
        teaser = f"{count} tracks de plus reservees aux membres du circuit."

    plaintext_obj = {"fragments": fragments, "source": clear}
    plaintext = json.dumps(plaintext_obj, ensure_ascii=False).encode("utf-8")

    salt, iv, ct = encrypt(plaintext, code)

    content["circuit"] = {
        "v": 1,
        "kid": kid,
        "salt": base64.b64encode(salt).decode("ascii"),
        "iv": base64.b64encode(iv).decode("ascii"),
        "ct": base64.b64encode(ct).decode("ascii"),
        "teaser": teaser,
        "count": count,
    }

    content_path.write_text(
        json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"[OK] content/{num:02d}.json : champ 'circuit' ecrit "
        f"({count} track(s), kid={kid!r}, {len(fragments)} fragment(s))."
    )


def _decrypt_circuit(circuit: dict, code: str) -> dict:
    """Decode base64 + dechiffre le blob "circuit", renvoie le plaintext
    parse en dict. Sort proprement (exit 1, message clair) sur code faux,
    blob corrompu ou champ manquant."""
    _crypto()
    try:
        salt = base64.b64decode(circuit["salt"])
        iv = base64.b64decode(circuit["iv"])
        ct = base64.b64decode(circuit["ct"])
    except KeyError as e:
        print(f"[ERR] champ 'circuit' incomplet : {e} manquant.", file=sys.stderr)
        sys.exit(1)

    try:
        plaintext = decrypt(salt, iv, ct, code)
    except Exception:
        print(
            "[ERR] code incorrect ou blob 'circuit' corrompu "
            "(echec du dechiffrement).",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("[ERR] le clair dechiffre n'est pas un JSON valide.", file=sys.stderr)
        sys.exit(1)


def cmd_open(num: int, code: str):
    """Dechiffre content/NN.json.circuit et recree content/circuit/NN.json
    a partir du champ "source" du clair. Refuse si content/circuit/NN.json
    existe deja (pas d'ecrasement silencieux)."""
    content_path = _content_path(num)
    clear_path = _circuit_clear_path(num)

    if clear_path.exists():
        print(
            f"[ERR] content/circuit/{num:02d}.json existe deja : refus "
            "d'ecraser (supprime-le d'abord si tu veux le regenerer).",
            file=sys.stderr,
        )
        sys.exit(1)
    if not content_path.exists():
        print(f"[ERR] content/{num:02d}.json introuvable.", file=sys.stderr)
        sys.exit(1)

    content = json.loads(content_path.read_text(encoding="utf-8"))
    circuit = content.get("circuit")
    if not circuit:
        print(f"[ERR] content/{num:02d}.json n'a pas de champ 'circuit'.", file=sys.stderr)
        sys.exit(1)

    plaintext_obj = _decrypt_circuit(circuit, code)
    source = plaintext_obj.get("source")
    if source is None:
        print(
            "[ERR] le clair dechiffre n'a pas de champ 'source' "
            "(blob cree avant l'ajout du round-trip ?).",
            file=sys.stderr,
        )
        sys.exit(1)

    CIRCUIT_DIR.mkdir(parents=True, exist_ok=True)
    clear_path.write_text(
        json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] content/circuit/{num:02d}.json recree depuis le blob chiffre.")


def cmd_check(num: int, code: str):
    """Dechiffre et verifie l'integrite du circuit : fragments non vides,
    positions entieres. Exit 0 si valide, 1 sinon (message clair)."""
    content_path = _content_path(num)
    if not content_path.exists():
        print(f"[ERR] content/{num:02d}.json introuvable.", file=sys.stderr)
        sys.exit(1)

    content = json.loads(content_path.read_text(encoding="utf-8"))
    circuit = content.get("circuit")
    if not circuit:
        print(f"[ERR] content/{num:02d}.json n'a pas de champ 'circuit'.", file=sys.stderr)
        sys.exit(1)

    plaintext_obj = _decrypt_circuit(circuit, code)
    fragments = plaintext_obj.get("fragments")
    if not fragments:
        print("[ERR] aucun fragment dans le clair dechiffre.", file=sys.stderr)
        sys.exit(1)

    errors = []
    for i, frag in enumerate(fragments):
        position = frag.get("position")
        html_fragment = frag.get("html")
        if not isinstance(position, int):
            errors.append(f"fragment {i} : 'position' n'est pas un entier ({position!r})")
        if not html_fragment or not html_fragment.strip():
            errors.append(f"fragment {i} : 'html' est vide")

    if errors:
        print(f"[ERR] {len(errors)} probleme(s) dans le circuit N°{num:02d} :", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"[OK] Circuit N°{num:02d} valide : {len(fragments)} fragment(s), code correct."
    )


def gen_code(num: int = None) -> str:
    """Propose un code aleatoire 'mot-mot-mot-NN' via secrets (3 mots pioches
    dans WORDLIST + un numero a 2 chiffres, fourni ou tire au hasard)."""
    words = [secrets.choice(WORDLIST) for _ in range(3)]
    if num is None:
        num = secrets.randbelow(90) + 10  # 10..99
    return "-".join(words) + f"-{num:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="Scelle/ouvre le contenu chiffre 'circuit ferme' d'une issue."
    )
    parser.add_argument("--seal", type=int, metavar="NN", help="Chiffre content/circuit/NN.json dans content/NN.json")
    parser.add_argument("--open", type=int, metavar="NN", help="Dechiffre content/NN.json vers content/circuit/NN.json")
    parser.add_argument("--check", type=int, metavar="NN", help="Verifie l'integrite du circuit chiffre")
    parser.add_argument("--code", help="Code membre (requis avec --seal/--open/--check)")
    parser.add_argument("--kid", help="Identifiant de cle (defaut : deduit de date_iso, format YYYY-MM)")
    parser.add_argument("--teaser", help="Texte public teaser (defaut : construit depuis le nombre de tracks)")
    parser.add_argument("--gen-code", action="store_true", help="Propose un code aleatoire mot-mot-mot-NN")
    parser.add_argument("--num", type=int, metavar="NN", help="Numero utilise dans --gen-code (optionnel, sinon tire au hasard)")
    args = parser.parse_args()

    if args.gen_code:
        print(gen_code(args.num))
        return

    if args.seal is not None:
        if not args.code:
            parser.error("--seal necessite --code")
        cmd_seal(args.seal, args.code, kid=args.kid, teaser=args.teaser)
        return

    if args.open is not None:
        if not args.code:
            parser.error("--open necessite --code")
        cmd_open(args.open, args.code)
        return

    if args.check is not None:
        if not args.code:
            parser.error("--check necessite --code")
        cmd_check(args.check, args.code)
        return

    parser.error("Choisis une action : --seal, --open, --check ou --gen-code.")


if __name__ == "__main__":
    main()
