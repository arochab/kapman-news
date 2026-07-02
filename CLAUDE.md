# KAPMAN SIGNAL — Agent Instructions

KAPMAN SIGNAL is an underground-electronic music newsletter distributed as a
**Progressive Web App with Web Push** — not email. Static issues on GitHub Pages,
push notifications via a Flask server on Render. 100% free to run.

Audience: portfolio/showcase piece + ~10–30 close friends of the Escape Music
Collective (Paris). Mobile-first reading.

## Architecture (don't re-derive — it's settled)

```
GitHub Pages (static site)  +  Render (Flask push server)  +  Gist (subscriber store)
```

- **`service-worker.js` lives at the repo ROOT** — never move it into `pwa/`, or its
  scope won't cover `/issues/` and subscriptions silently break.
- **`pwa/push-client.js`** is the shared push JS. It computes the site root dynamically
  so the SW registers at the right scope from any page depth.
- **Server** `server/app.py` on Render (`gunicorn app:app`, root dir `server/`).
  Subscriptions persist in a **private GitHub Gist** via the API (env: `GITHUB_TOKEN`
  scope `gist`, `GIST_ID`). Plus `VAPID_PRIVATE_KEY` (PEM — the server converts it to
  the raw 32-byte scalar that pywebpush needs), `VAPID_PUBLIC_KEY`, `PUSH_SECRET`, `PORT`.
- **Publishing** = push an `issues/NN/index.html`. La notification ne part PLUS
  au push : `.github/workflows/scheduled-notify.yml` envoie la dernière issue
  non notifiée chaque **mardi et vendredi à 10h (Paris)** — marqueur dans
  `state/last-notified-issue.txt`, commité après envoi réussi. Envoi manuel
  immédiat possible via `notify.yml` (workflow_dispatch, input `issue`).
  Pour re-render des issues existantes (refonte template) :
  `python tools/build_issue.py --rebuild-all` + commit `[skip notify]`.
- **Cadence** : scaffold auto du numéro suivant (scaffold.yml) mardi & vendredi
  ~10h45 Paris ; l'écriture éditoriale reste manuelle (Adam en session).

## Authoring a new issue

1. `python tools/new_issue.py --num NN` → scaffolds `content/NN.json`.
2. Fill the content (this is the editorial step — done in session).
3. `python tools/new_issue.py --num NN --build` → renders `issues/NN/index.html`
   from `templates/issue.html.j2` and updates the home list.
4. Commit + push → notification fires automatically.

## Editorial rules (hard constraints)

- **Never repeat** a track, artist, or label used in a previous issue. Cross-reference
  the track history before writing (kept in the user's memory).
- **Real links only** — YouTube/Bandcamp links come from Adam's actual playlists, never
  invented or guessed.
- **Doctrine de liens** : chaque track vise `▶ Écouter` (YouTube) + `↗ Bandcamp`
  (sorties actuelles) ou `◈ Discogs` (catalogue — la release exacte), sourcés à l'écriture.
- **Méta structurée** : utiliser les champs optionnels `label`/`catno`/`year`/`place`/
  `format` du schéma track (cf `content/SCHEMA.md`) ; jamais une méta sans label ni année.
- La tagline doit être **tenue par le séquencement** (si le titre annonce Cologne, la
  tracklist y arrive). Max ~1 référence pointue par description de track ; le résumé
  « Cette édition » vend l'écoute, pas la cuisine interne.
- **Fact-check Discogs bloquant** avant publication : chaque méta (label, catno, année,
  ville) vérifiée sur la release exacte. Une méta fausse devant des diggers est
  disqualifiante (cf `docs/AUDIT-EDITORIAL.md` §2 — erreurs relevées dans 09/10).
- **Zéro cuisine interne dans le texte publié** : jamais « tes playlists », « zéro
  répétition avec N°0X », noms d'outils (IA, scripts) dans la note de studio, ou
  auto-commentaire de fabrication (« deux sorties du même label — c'est pas un hasard »).
- **Règle du canon : max 1 track canon par numéro**, uniquement au service d'une track
  obscure. Le N°09 (Metromusic, Remote, WIG001) est le modèle ; pas le N°10.
- **Tics bannis** : « exactement » (quota 0), « niveau d'exigence » recyclé, compteurs
  de vues YouTube comme preuve de goût (1 max/numéro). Varier les thèses de la note de
  studio. Stats = vraie donnée (copies, prix, durée) — jamais une date Wikipédia.
- Les créneaux mar/ven sont des **fenêtres de livraison, pas des quotas** : ne publier
  que ce qui est au niveau. Stratégie produit/monétisation : `docs/AUDIT-EDITORIAL.md`.
- Section accents cycle red → green → blue. Stats alternate green/blue. L'accent
  dominant d'une issue (numéral géant, CTA écoute) est dérivé de `issue_num % 3`
  par le template — rien à décider par issue.
- Tone: euphoric · physical · precise. KAPMAN = the person; Escape Music Collective =
  the place. Never confuse the two.

## Gotchas already solved (see memory)

- SW scope (root, not `pwa/`).
- VAPID private key = raw 32-byte scalar base64url, not PEM/DER (server converts).
- `sent:1` but nothing received = Chrome's Android-level notification permission was off
  (two permission layers: the site *and* Chrome itself).
- **Render free tier cold start > 30s** = la notif N°10 a raté sur ReadTimeout (juin 2026).
  `tools/send_push.py` fait maintenant warm-up (~180s max) + timeout 120s + 3 retries, et
  `server/gunicorn.conf.py` monte le timeout worker à 120s (le défaut 30s tuait le worker
  en plein envoi). La start command Render doit rester `gunicorn app:app` (conf auto-chargée).

## Design system

Ink `#0E0F14` · Cream `#F0EEE6` · Red `#E83A2E` · Green `#1FC85E` · Blue `#3A6CF0`
(couleurs exactes du brand book `brand_assets/`). Fonts : **Black Ops One** (logo/display
uniquement) · **Hanken Grotesk** (texte) · **IBM Plex Mono** (technique). Gris uniquement
via les tokens du `:root` (`--dim`/`--meta`/`--faint`, tous ≥4.5:1 sur l'ink) — zéro hex
littéral hors `:root`. Logo = three additive-light circles. All design lives in
`templates/issue.html.j2` — change it there, never per-issue.
