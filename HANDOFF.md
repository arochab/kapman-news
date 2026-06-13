# Session Handoff — reprise de contexte

> Ce fichier permet de reprendre le travail de façon transparente quand on
> rouvre `kapman-news` dans une nouvelle session VSCode.

## Où on en est (état au 2026-06-13 — release v1.0.0)

Le système **KAPMAN SIGNAL est entièrement opérationnel, déployé, et la DA est
alignée sur le brand book** :

- **Site live** : https://arochab.github.io/kapman-news/ (GitHub Pages, `master`)
- **Serveur push live** : https://kapman-news.onrender.com (Flask + pywebpush, persistence Gist)
- **Push testé et reçu de bout en bout** sur Pixel / Chrome.
- **1 abonné** (Adam), Gist privée.

### DA (refonte de cette session — voir mémoire `kapman_brand_system`)
- Typo du brand book : **Black Ops One** (logo KAPMAN UNIQUEMENT), **Hanken Grotesk**
  (texte), **IBM Plex Mono** (méta/headings/stats/abonnement).
- Couleurs exactes : red #E83A2E, green #1FC85E, blue #3A6CF0, ink #0E0F14, cream #F0EEE6.
- Logo = vrai mélange additif de lumière (screen → jaune/cyan/blanc aux intersections).
- Anim : SONIC MARK · RGB SPLIT sur le wordmark, reveals au scroll (robustes : le
  contenu reste visible si le JS échoue — gaté par `.js` + filet de sécurité).
- QR d'abonnement centré en bas. Footer au contraste lisible.

### Pièges d'infra résolus cette session (voir mémoire `kapman_news_infra`)
- `notify.yml` écoutait `branches: [main]` alors que le repo est sur `master` →
  **la notif auto ne partait jamais.** Corrigé en `[master]` + ajout `workflow_dispatch`
  (`gh workflow run notify.yml -f issue=NN` pour renvoyer une notif).
- Abonnés morts (410 Gone) pas purgés à cause d'une particularité pywebpush
  (`ex.response` None). Corrigé : détection du 410 dans le message → purge auto.

## Ce qui peut venir ensuite

1. **Issue N°10** — quand Adam veut. Workflow ci-dessous.
2. **Fréquence bi-hebdomadaire** (2×/semaine) — discuté en fin de session v1 ; à cadrer
   (rythme éditorial soutenu : ~8 tracks no-repeat par issue, voir track history).
3. **Supprimer NEWSLETTER DEMO** (ancien pipeline Gmail/FLUX) — sur feu vert explicite
   d'Adam uniquement. Tout a déjà migré ici.

## Comment publier la prochaine issue (rappel)

```bash
python tools/new_issue.py --num 10            # scaffold content/10.json
# remplir le contenu (no-repeat — voir newsletter_track_history en mémoire)
python tools/new_issue.py --num 10 --build    # rendu + maj home
git add -A && git commit -m "KAPMAN SIGNAL N°10" && git push   # notif auto (master)
```
