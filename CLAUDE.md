# CIRCUIT FERMÉ (ex KAPMAN SIGNAL) — Agent Instructions

CIRCUIT FERMÉ is an underground-electronic music newsletter distributed as a
**Progressive Web App with Web Push** — not email. Static issues on GitHub Pages,
push notifications via a Flask server on Render. 100% free to run.

Audience: portfolio/showcase piece + ~10–30 close friends (Paris). Mobile-first.

## Brand (règle stricte depuis juillet 2026)
- La marque publique est **CIRCUIT FERMÉ**. Ni « KAPMAN » ni « Escape Music
  Collective » n'apparaissent dans la marque, les titres, les notifications ou le
  corps des textes (Adam ne veut pas se griller).
- Seule exception : le crédit discret du footer : « Sélection · KAPMAN » avec trois
  liens : Shotgun `https://shotgun.live/artists/kapman_music`, SoundCloud
  `https://soundcloud.com/kapman_music`, Instagram `https://www.instagram.com/kapman___/`.

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
- **Publishing = committer un `content/NN.json` REMPLI suffit.** Au créneau
  suivant (mardi/vendredi 10h Paris), `scheduled-notify.yml` prend le plus
  petit numéro rempli non notifié, le REND si besoin (build committé par le
  bot), envoie la notification et avance `state/last-notified-issue.txt`.
  File FIFO, un numéro par créneau, squelette vide = jamais envoyé. Envoi
  manuel immédiat : `notify.yml` (workflow_dispatch, input `issue`). Refonte
  template : `python tools/build_issue.py --rebuild-all` + commit
  `[skip notify]`. Processus complet : `docs/PIPELINE-EDITORIAL.md`.
- **Anti-répétition** : `python tools/track_history.py` (`--check "Nom"`)
  avant toute sélection.
- **Cadence** : scaffold auto du numéro suivant (scaffold.yml) mardi & vendredi
  ~10h45 Paris ; l'écriture éditoriale se fait en session sur cette base.

## Authoring a new issue

1. `python tools/new_issue.py --num NN` → scaffolds `content/NN.json`.
2. Fill the content (this is the editorial step — done in session).
3. `python tools/new_issue.py --num NN --build` → renders `issues/NN/index.html`
   from `templates/issue.html.j2` and updates the home list.
4. Commit + push → notification fires automatically.

## Editorial rules (hard constraints)

- **Never repeat** : aucun track, artiste ou label d'une édition précédente ne peut
  revenir avant **10 éditions d'intervalle** (ex : utilisé au N°09, libre au N°19).
  Vérifier avec `python tools/track_history.py --check "Nom"` avant toute sélection.
- **Real links only** : chaque lien YouTube/Bandcamp/Discogs vérifié pendant l'écriture
  (oembed + api.discogs.com), jamais inventé ni deviné.
- **Les playlists d'Adam (`content/playlists/*.txt`) sont un PROFIL DE GOÛT et une
  BLOCKLIST, jamais une source** : Adam connaît déjà ces sons. Tout track ou artiste
  qui y figure est INTERDIT de sélection (vérif : `grep -i "<artiste>"
  content/playlists/*.txt` doit être vide). La mission : des découvertes nouvelles
  dans ce goût (autres références des mêmes labels, labels adjacents, même époque).
- **Profil de goût d'Adam (source : ses playlists — s'y tenir)** : tech house UK
  1996-2007 (Wiggle-adjacent, Terry Francis, Swag, 20:20 Vision, Sonambulist, Cubic,
  Whiff), minimal/tech house allemande 2001-2007 (KarateMusik, Ringelbeatz,
  38db-Tonsportgruppe, Satt, i220, Disko B, Tiny Sticks, Freude Am Tanzen),
  electro/tech house hybride, progressive house UK 1998-2005, acid revival mi-2000s,
  edits (Clone, DFA), rominimal et scène actuelle (Jamuse, Planka, Dank, Vanni Danni).
  PAS de French house filtrée, PAS de canon Chicago/Detroit sauf au service d'une
  obscurité.
- **AUCUN tiret dans tout texte publié ni dans les réponses à Adam** : ni « — » ni
  « – », nulle part (prose, titres, noms de tracks, UI). Séparateur artiste/titre :
  « · ». Les traits d'union de mots composés français restent normaux.
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

Ink `#0E0F14` · Cream `#F0EEE6` · Red `#E83A2E` · Green `#1FC85E` · Blue `#3A6CF0`.
Fonts : **Hanken Grotesk** (texte + wordmark 800) · **IBM Plex Mono** (technique).
Black Ops One est SUPPRIMÉE (juillet 2026, demande d'Adam). Logo v3 = glyphe
« signal » (3 barres verticales arrondies R/V/B, hauteurs 12/22/17) + wordmark
KAPMAN (Hanken 800) + SIGNAL (mono espacé) ; plus de cercles additifs, plus de
glitch RGB. La triple-rule R/V/B reste la signature graphique. Gris uniquement
via les tokens du `:root` (`--dim`/`--meta`/`--faint`, tous ≥4.5:1 sur l'ink) : zéro hex
littéral hors `:root`. All design lives in
`templates/issue.html.j2` — change it there, never per-issue.
