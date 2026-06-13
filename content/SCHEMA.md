# Schéma d'une issue — `content/NN.json`

Chaque issue est décrite par un JSON. `build_issue.py` le transforme en
`issues/NN/index.html` via `templates/issue.html.j2` (DA garantie identique).

## Champs racine

| Champ | Type | Description |
|-------|------|-------------|
| `issue_num` | int | Numéro de l'issue (9 → affiché "N°09") |
| `date_iso` | str | Date ISO `YYYY-MM-DD` (méta du hero) |
| `month_label` | str | Ex. `"Juin 2026"` |
| `reading_time` | str | Ex. `"4 min"` |
| `tagline_plain` | str | Titre texte brut (utilisé dans `<title>` + liste home) |
| `tagline_html` | str | Titre hero, peut contenir `<br>` |
| `summary_bullets` | list[str] | Puces "Cette édition" |
| `blocks` | list | Corps : alternance de `section` et `stat` dans l'ordre |
| `forward_text` | str | Paragraphe "Ce qui suit" (HTML autorisé) |

## Blocs

### `section` avec tracks
```json
{
  "type": "section",
  "accent": "red",          // red | green | blue
  "heading": "Ce qui tourne — les incontournables",
  "tracks": [
    {
      "name": "Artiste — Titre",
      "meta": "Label · Année",        // optionnel
      "body": "Description...",         // HTML autorisé (liens ok)
      "links": [
        { "label": "▶ Écouter", "url": "https://youtube.com/..." },
        { "label": "↗ Bandcamp", "url": "https://..." }
      ]
    }
  ]
}
```

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

## Règles éditoriales (voir mémoire)
- **Jamais** répéter un track/artiste/label déjà publié → cf
  `NEWSLETTER DEMO/memory/newsletter_track_history.md`.
- **Liens YouTube réels uniquement**, issus des playlists CSV. Ne jamais inventer.
- L'accent des sections suit l'ordre rouge → vert → bleu → rouge.
- Les `stat` reprennent l'accent vert/bleu en alternance.
