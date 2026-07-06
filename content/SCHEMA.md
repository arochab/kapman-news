# Schéma d'une issue — `content/NN.json`

Chaque issue est décrite par un JSON. `build_issue.py` le transforme en
`issues/NN/index.html` via `templates/issue.html.j2` (DA garantie identique).

## Champs racine

| Champ | Type | Description |
|-------|------|-------------|
| `issue_num` | int | Numéro de l'issue (9 → affiché "N°09"). Détermine aussi l'accent d'issue (`issue_num % 3` → rouge/vert/bleu) appliqué au numéral géant, au kicker du summary, à la sélection de texte et au bouton d'écoute. |
| `date_iso` | str | Date ISO `YYYY-MM-DD` (méta du hero) |
| `month_label` | str | Ex. `"Juin 2026"` |
| `reading_time` | str | Ex. `"4 min"` |
| `tagline_plain` | str | Titre texte brut (utilisé dans `<title>` + liste home) |
| `tagline_html` | str | Titre hero (`<h1>`), peut contenir `<br>` |
| `summary_bullets` | list[str] | Puces "Cette édition". Les N premières (N = nombre de sections) sont des liens `#s1`, `#s2`, … vers les sections correspondantes. |
| `blocks` | list | Corps : alternance de `section` et `stat` dans l'ordre |
| `forward_text` | str | Paragraphe "Ce qui suit" (HTML autorisé) |
| `playlist_url` | str | *Optionnel.* Lien "Écouter la sélection" · prime sur `listen_all_url` (calculé par le build à partir des liens YouTube des tracks, nommé automatiquement « CIRCUIT FERMÉ · N°NN · tagline » via le paramètre `title`). Pour une vraie playlist YouTube pérenne, la créer sur le compte anonyme et la nommer selon la même convention avant de coller son URL ici. |
| `listening_time` | str | *Optionnel.* Ex. `"22 min"`. Si présent, le hero affiche `{{ reading_time }} lecture · {{ listening_time }} écoute` au lieu du format par défaut. |
| `show_tracklist` | bool | *Optionnel.* Si vrai, ajoute un récap mono "Tracklist" (toutes les tracks, toutes sections confondues) juste avant "Ce qui suit", chaque ligne pointant vers l'ancre `#{{ t.slug }}` de la track. |

Champs vides (`""`, `null`, absents) = falsy en Jinja : ignorés proprement, aucune
adaptation nécessaire pour les anciennes issues (09, 10, …).

## Blocs

Chaque bloc `section` accepte en plus un champ optionnel `invert` :

| Champ | Type | Description |
|-------|------|-------------|
| `invert` | bool | *Optionnel.* Force le rendu en panneau cream inversé (fond clair, texte encre). La section `"Note de studio"` bascule automatiquement en inversé même sans ce flag (détection par titre). |

### `section` avec tracks
```json
{
  "type": "section",
  "accent": "red",          // red | green | blue
  "heading": "Ce qui tourne — les incontournables",
  "invert": false,          // optionnel
  "tracks": [
    {
      "name": "Artiste — Titre",
      "meta": "Label · Année",        // optionnel, fallback si label/catno/year absents
      "label": "Trax Records",        // optionnel
      "catno": "TX127",               // optionnel
      "format": "12\"",               // optionnel
      "place": "Chicago",             // optionnel
      "year": "1986",                 // optionnel
      "body": "Description...",         // HTML autorisé (liens ok)
      "dig": "Pour creuser : ...",     // optionnel — aparté "↳" sous la description
      "links": [
        { "label": "▶ Écouter", "url": "https://youtube.com/..." },
        { "label": "↗ Bandcamp", "url": "https://..." }
      ]
    }
  ]
}
```

`t.slug` n'est **pas** un champ éditorial : il est calculé par `build_issue.py`
(slugification de `name`) et sert d'ancre `#slug` pour la track (ciblée par le
récap tracklist et par des liens externes). Rien à saisir à la main.

#### Convention méta (label/catno/year/place/format)

Si au moins un des champs structurés `label`, `catno` ou `year` est présent,
le rendu structuré remplace `meta` :

```
{{ label }} {{ catno }} · {{ format }} · {{ place }} · {{ year }}
```

(chaque segment n'apparaît que s'il est renseigné). Sinon, `meta` (chaîne
libre existante) sert de repli — c'est le format utilisé par toutes les
issues antérieures à la v2, aucune migration requise.

### `section` avec paragraphes (label du mois, note de studio)
```json
{
  "type": "section",
  "accent": "blue",
  "heading": "Label du mois — ...",
  "paragraphs": [
    "Paragraphe 1 (HTML autorisé, liens ok).",
    "Paragraphe 2 avec <a href=\"...\" target=\"_blank\">un lien →</a>"
  ]
}
```

### `stat` (callout chiffre)
```json
{
  "type": "stat",
  "accent": "green",        // red | green | blue
  "number": "1996",
  "context": "Contexte du chiffre..."
}
```

## Doctrine des liens

Chaque track vise, dans cet ordre de priorité :

- **`▶ Écouter`** — lien YouTube, systématique, sourcé dans les playlists réelles.
- **`↗ Bandcamp`** — pour les sorties actuelles (disponibles à l'achat/écoute directe).
- **`◈ Discogs`** — pour le catalogue (pressages anciens, épuisés, référence discographique).

Liens réels uniquement — jamais inventés ni devinés (cf. règle éditoriale
ci-dessous). Le label du lien porte son propre symbole (`▶`, `↗`, `◈`) ; le
template ne les ajoute pas automatiquement.

## Numéro à circuit fermé

Mécanisme freemium : une issue peut embarquer du contenu membre chiffré côté
client (AES-256-GCM, clé dérivée d'un code par PBKDF2, compatible WebCrypto),
déchiffré dans le navigateur par un code jamais commité. Piloté par
`python tools/circuit.py` (`--seal` / `--check` / `--open` / `--gen-code`).

### Le clair membre : `content/circuit/NN.json`

Fichier gitignoré (`content/circuit/`), n'existe qu'en session d'écriture,
jamais commité. Structure :

```json
{
  "blocks": [
    {
      "type": "section",
      "accent": "red",
      "heading": "Titre du bloc membre",
      "position": 2,
      "tracks": [ /* même structure qu'un track public, cf plus haut */ ]
    },
    {
      "type": "stat",
      "accent": "blue",
      "number": "1996",
      "context": "Contexte du chiffre...",
      "position": 4
    }
  ]
}
```

Chaque bloc a la **même structure qu'un bloc public** (section avec `tracks`
ou `paragraphs`, ou `stat` ; cf sections « Blocs » plus haut), plus un champ
entier obligatoire `position` : le fragment rendu est inséré après l'élément
public portant `data-flow="position"` (`position` = 0 : juste après le hero,
avant le premier bloc public).

### Le blob chiffré : champ `circuit` de `content/NN.json`

```json
{
  "v": 1,
  "kid": "2026-07",
  "salt": "<base64>",
  "iv": "<base64>",
  "ct": "<base64>",
  "teaser": "3 pièces, la sélection par où commencer et le récapitulatif complet sont scellés. La note de studio et 1 statistique restent publiques.",
  "count": 3,
  "pieces": [
    { "idx": 4, "year": "2000", "format": "12\"" },
    { "idx": 6, "format": "12\"" }
  ],
  "total": 7
}
```

| Champ | Description |
|-------|-------------|
| `v` | Version du format (toujours `1` actuellement). |
| `kid` | Identifiant de clé, format `YYYY-MM`. Défaut : déduit de `date_iso` de l'issue. |
| `salt` | Sel PBKDF2, 16 octets aléatoires, base64 standard. |
| `iv` | Vecteur d'initialisation AES-GCM, 12 octets aléatoires, base64 standard. |
| `ct` | Ciphertext AES-256-GCM, tag concaténé en fin (comportement par défaut de `cryptography` et de WebCrypto), base64 standard. |
| `teaser` | Texte public affiché à la place du contenu membre (chaîne libre publique, jamais chiffrée). Écrit par `--seal --teaser "..."`, sinon construit automatiquement depuis `count`. |
| `count` | Nombre total de tracks des blocs membres. Calculé par `--seal`, jamais saisi à la main. |
| `pieces` | **Public, jamais chiffré.** Registre caviardé : liste ordonnée des pièces membres, `{"idx": <index global 1..total>, "year"?: "...", "format"?: "..."}`. `year`/`format` omis si absents du track source. **JAMAIS** `name`/`label`/`catno`/`place` ni aucun texte — seule une méta qui ne désanonymise pas la track. Calculé par `--seal` (`compute_pieces`), jamais saisi à la main. |
| `total` | Nombre total de pièces du numéro (tracks publiques + tracks membres), calculé par `--seal`. |

Absent (issue sans circuit fermé) : `circuit` est falsy en Jinja, rendu
identique à aujourd'hui, aucune adaptation nécessaire pour les anciennes
issues. De même, `pieces`/`total` absents (blob scellé avant leur
introduction) : le template affiche le seuil sans lignes caviardées, teaser
seul — un `--seal` de plus les régénère.

### L'index global des pièces (`idx` / `start_idx`)

`--seal` calcule (fonction `compute_pieces` de `tools/circuit.py`) l'index
global 1-based de chaque **pièce** (= une track, publique ou membre) dans
l'ordre exact où la page finale les affiche :

1. Le flux public est la liste `blocks` de `content/NN.json`, dans l'ordre ;
   chaque bloc y occupe la position de flux `data-flow="{{ loop.index }}"`
   (1-based, voir `templates/issue.html.j2`), la position `0` étant juste
   avant le premier bloc public (immédiatement après le hero).
2. Chaque bloc membre porte son champ `position` (même index de flux) : il
   s'insère juste **après** le bloc public de ce numéro (`position: 0` =
   avant le premier bloc public).
3. À position égale, plusieurs blocs membres conservent l'ordre dans lequel
   ils apparaissent dans `content/circuit/NN.json` (stable).
4. Seuls les blocs `section` munis de `tracks` produisent des pièces (une
   par track) ; les `stat` et les sections à paragraphes (label du mois,
   note de studio) n'en produisent aucune.
5. On numérote `1..total` en parcourant ce flux dans l'ordre d'affichage :
   blocs membres `position: 0`, puis bloc public 1, blocs membres
   `position: 1`, bloc public 2, blocs membres `position: 2`, etc.

Chaque fragment du plaintext déchiffré (`fragments[]`, cf ci-dessous) reçoit
en plus un champ `start_idx` : l'index global de la première track de son
bloc (absent/`null` si le bloc n'a pas de tracks). `templates/circuit_fragment`
numérote ainsi « PIÈCE `start_idx + i` / `total` » pour la i-ème track du
fragment (0-based), sans recalculer l'algorithme côté client.

### Crypto (compatibilité WebCrypto obligatoire)

- Clé : `PBKDF2-HMAC-SHA256(code normalisé, salt, 310000 itérations, 32 octets)`.
- Normalisation du code : `strip()` puis minuscule, rien d'autre.
- Chiffrement : AES-256-GCM, IV 12 octets aléatoires, tag concaténé en fin de
  ciphertext.
- Encodage : base64 standard avec padding pour `salt`/`iv`/`ct`.
- Le plaintext (avant chiffrement) est un JSON UTF-8 :
  `{"fragments": [{"position": <int>, "html": "<fragment HTML rendu>", "start_idx": <int|null>}], "source": {...}}`
  où `fragments[].html` vient du rendu individuel de chaque bloc via
  `templates/circuit_fragment.html.j2`, `fragments[].start_idx` est l'index
  global (1-based) de la première track du bloc (`null` si le bloc n'a pas
  de tracks, cf section précédente sur `compute_pieces`), et `source` est le
  contenu intégral de `content/circuit/NN.json` (permet à `--open` de
  reconstruire le clair sans perte).

### Procédure

1. Écrire le clair dans `content/circuit/NN.json` (même règles éditoriales
   que le contenu public : anti-répétition, liens réels, méta structurée).
2. `python tools/circuit.py --seal NN --code "mot-mot-mot-NN"` : rend les
   fragments, chiffre, écrit le champ `circuit` dans `content/NN.json`.
   Code de test rapide : `python tools/circuit.py --gen-code`.
3. `python tools/circuit.py --check NN --code "..."` : vérifie l'intégrité
   avant publication (fragments non vides, positions entières, code correct).
4. Commit **sans** `content/circuit/NN.json` (gitignoré, le clair ne quitte
   jamais la session). Le code membre n'est jamais commité non plus ; il se
   transmet aux membres par un canal séparé.
5. Pour retoucher un circuit déjà scellé : `python tools/circuit.py --open NN
   --code "..."` recrée `content/circuit/NN.json` à partir du blob chiffré
   (refuse si le fichier existe déjà, pour ne rien écraser). Éditer, puis
   `--seal` de nouveau.

**Rappel** : le code n'est jamais commité, aucun clair membre ne doit
apparaître dans git (le `.gitignore` couvre `content/circuit/`, mais rester
vigilant sur les diffs avant `git add`).

## Règles éditoriales (voir mémoire)
- **Jamais** répéter un track/artiste/label déjà publié → cf
  `NEWSLETTER DEMO/memory/newsletter_track_history.md`.
- **Liens YouTube réels uniquement**, issus des playlists CSV. Ne jamais inventer.
- L'accent des sections suit l'ordre rouge → vert → bleu → rouge.
- Les `stat` reprennent l'accent vert/bleu en alternance.
