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
| `playlist_url` | str | *Optionnel.* Lien "Écouter la sélection" — prime sur `listen_all_url` (calculé par le build à partir des liens YouTube des tracks). |
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

## Règles éditoriales (voir mémoire)
- **Jamais** répéter un track/artiste/label déjà publié → cf
  `NEWSLETTER DEMO/memory/newsletter_track_history.md`.
- **Liens YouTube réels uniquement**, issus des playlists CSV. Ne jamais inventer.
- L'accent des sections suit l'ordre rouge → vert → bleu → rouge.
- Les `stat` reprennent l'accent vert/bleu en alternance.
