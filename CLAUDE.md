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
- **Publishing** = push an `issues/NN/index.html`; `.github/workflows/notify.yml` calls
  `/notify` → Web Push to all subscribers.

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
- Section accents cycle red → green → blue. Stats alternate green/blue.
- Tone: euphoric · physical · precise. KAPMAN = the person; Escape Music Collective =
  the place. Never confuse the two.

## Gotchas already solved (see memory)

- SW scope (root, not `pwa/`).
- VAPID private key = raw 32-byte scalar base64url, not PEM/DER (server converts).
- `sent:1` but nothing received = Chrome's Android-level notification permission was off
  (two permission layers: the site *and* Chrome itself).

## Design system

Ink `#0D0D0D` · Cream `#F5F0E8` · Red `#E8372A` · Green `#00A650` · Blue `#2F57D4`.
Logo = three additive-light circles. Font: Space Grotesk. All design lives in
`templates/issue.html.j2` — change it there, never per-issue.
