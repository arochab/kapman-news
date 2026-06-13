# Session Handoff — reprise de contexte

> Ce fichier permet de reprendre le travail de façon transparente quand on
> rouvre `kapman-news` dans une nouvelle session VSCode. Une fois le contexte
> bien repris, ce fichier peut être supprimé (ou gardé comme journal).

## Où on en est (état au 2026-06-13)

Le système **KAPMAN SIGNAL est entièrement opérationnel et déployé** :

- **Site live** : https://arochab.github.io/kapman-news/ (GitHub Pages, branche `master`)
- **Serveur push live** : https://kapman-news.onrender.com (Flask + pywebpush, `persistence:gist`)
- **Push testé et reçu** sur Pixel 10 Pro / Chrome — toute la chaîne fonctionne de bout en bout.
- **1 abonné** enregistré (Adam), stocké durablement dans une Gist privée.
- **Repo documenté** : README (standard brandpulse), LICENSE MIT, CLAUDE.md, description + 10 topics GitHub.

L'architecture complète et les pièges résolus sont dans la mémoire
(`kapman_news_infra.md`) et résumés dans `CLAUDE.md`.

## Ce qu'on a décidé de faire ensuite

1. **Refaçonner la DA** ← prochaine grosse tâche, à cadrer ensemble.
   Adam veut faire évoluer le design. Le système actuel reproduit fidèlement le
   logo (3 cercles additifs) + palette, mais il veut aller plus loin.
   → Démarrer par : qu'est-ce qui doit changer ? (typo ? layout ? animations ?
   page d'accueil ? rendu des issues ?). Toute la DA vit dans
   `templates/issue.html.j2` (issues) et `index.html` (home).

2. **Supprimer NEWSLETTER DEMO** ← Adam le demandera plus tard, pas encore.
   C'est l'ancien pipeline Gmail/FLUX dans
   `...\SKOOL AI AUTOMATION\NEWSLETTER DEMO\`. Tout ce qui marche a déjà été
   migré ici — rien à récupérer de plus. Attendre le feu vert explicite d'Adam.

## Setup pour continuer (déjà fait, pour mémoire)

- VAPID, Render env vars, GitHub Actions secrets, UptimeRobot : tout est en place.
- La mémoire a été copiée vers le scope de ce dossier — elle est lue automatiquement.

## Comment publier la prochaine issue (rappel)

```bash
python tools/new_issue.py --num 10            # scaffold content/10.json
# remplir le contenu (no-repeat — voir newsletter_track_history en mémoire)
python tools/new_issue.py --num 10 --build    # rendu + maj home
git add -A && git commit -m "KAPMAN SIGNAL N°10" && git push   # notif auto
```
