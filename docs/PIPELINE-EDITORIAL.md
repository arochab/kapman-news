# PIPELINE ÉDITORIAL · comment un numéro s'écrit et part tout seul

Cadence : deux créneaux de livraison, mardi et vendredi 10h (Paris). Ce sont
des fenêtres, pas des quotas : la file s'écoule un numéro par créneau, dans
l'ordre, et un créneau sans numéro prêt reste silencieux.

## La chaîne, de bout en bout

1. **Source** : les playlists d'Adam dans `content/playlists/*.txt` (exports
   YouTube : URLs, labels, Discogs). C'est LA matière première des sélections.
   Aucun lien inventé, jamais.
2. **Anti-répétition** : `python tools/track_history.py` liste tout ce qui a
   déjà été utilisé (artistes, labels, tracks). `--check "Nom"` teste un
   candidat. À consulter AVANT de sélectionner.
3. **Curation** (session Claude, plan Fable puis exécution Sonnet) : choisir
   un thème non couvert et tenu par le séquencement, 7 tracks catalogue en
   ordre chronologique, 2 sorties récentes, 1 label. Profil de goût et règles
   dures dans CLAUDE.md (max 1 canon, zéro tiret, « exactement » quota 0,
   stats = vraie donnée, zéro cuisine interne).
4. **Vérification bloquante** pendant l'écriture : chaque lien YouTube via
   `https://www.youtube.com/oembed?url=<URL>&format=json` (le titre doit
   correspondre), chaque méta via `api.discogs.com` (le site web renvoie 403
   aux robots), chaque Bandcamp fetché. Champs structurés label/catno/year/
   place/format, jamais de méta devinée.
5. **Écriture** : remplir `content/NN.json` (squelette auto-créé par
   scaffold.yml après chaque créneau). Note de studio : première personne,
   matériel établi (TR-6S, MicroKorg 2, Live 12), thèse nouvelle par numéro.
6. **Publication et envoi : automatiques.** Committer le JSON rempli suffit.
   Au prochain créneau, `scheduled-notify.yml` prend le plus petit numéro
   rempli non notifié, le rend si besoin (build committé par le bot), envoie
   la notification et avance `state/last-notified-issue.txt`. Un squelette
   vide ne part jamais.
7. **Relecture d'Adam** : la fenêtre entre le commit du JSON et le créneau.
   Pour retenir un numéro : vider sa tagline ou repousser le commit.
   Pour envoyer sans attendre : Actions → « Push Notification · envoi
   manuel » → Run workflow avec le numéro.

## Garde-fous

- Rebuild de masse (refonte template) : `python tools/build_issue.py
  --rebuild-all` + commit `[skip notify]`. Le workflow d'envoi manuel ignore
  ces commits, et l'envoi programmé ne dépend que du marqueur.
- Un envoi raté (Render endormi, réseau) laisse le marqueur en place : le
  numéro repart au créneau suivant. `tools/send_push.py` fait warm-up,
  timeout long et retries ; `server/gunicorn.conf.py` tient le worker à 120s.
- La qualité prime sur la cadence : un numéro pas au niveau du N°09 attend.
