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

## Numéro à circuit fermé (à partir du N°17)

1. **Écrire les deux parties** : la partie publique dans `content/NN.json`
   comme d'habitude, la partie membre dans `content/circuit/NN.json`
   (gitignoré, jamais commité en clair). Même schéma de blocs que
   `content/SCHEMA.md`, plus un champ `position` par bloc pour indiquer où il
   s'insère dans le numéro reconstitué côté membre.
2. **Sceller** : `python tools/circuit.py --seal NN --code "<code du mois>"`
   puis vérifier avec `python tools/circuit.py --check NN`. Le scellé chiffré
   est embarqué dans la page publique ; le code du mois ne quitte jamais git.
   `--seal` produit aussi, en clair dans `content/NN.json`, le **registre
   caviardé public** (`circuit.pieces` : index global + méta sûre de chaque
   pièce membre, `circuit.total` : nb de pièces du numéro — jamais de
   nom/label/catno, cf `content/SCHEMA.md`). Si on réordonne les pièces
   (positions dans `content/circuit/NN.json`, ou tracks publiques
   ajoutées/retirées) : **re-seal obligatoire**, sinon le registre affiché
   ne correspond plus à l'ordre réel de la page.
3. **Committer** : uniquement `content/NN.json` et le scellé produit par
   `--seal` (embarqué dans le HTML rendu, registre `pieces`/`total` inclus).
   Ne jamais committer `content/circuit/NN.json` en clair ni le code du mois.
4. **Retoucher après coup** : `python tools/circuit.py --open NN --code
   "<code du mois>"` pour redéchiffrer localement, éditer, puis resceller
   (le re-seal régénère `pieces`/`total` depuis le contenu courant).
5. **Rendu et envoi restent automatiques** : la CI n'a jamais besoin du code
   du mois, elle ne touche qu'au HTML déjà scellé. `scheduled-notify.yml`
   fonctionne à l'identique pour un numéro fermé ou ouvert.

## Garde-fous

- Rebuild de masse (refonte template) : `python tools/build_issue.py
  --rebuild-all` + commit `[skip notify]`. Le workflow d'envoi manuel ignore
  ces commits, et l'envoi programmé ne dépend que du marqueur.
- Un envoi raté (Render endormi, réseau) laisse le marqueur en place : le
  numéro repart au créneau suivant. `tools/send_push.py` fait warm-up,
  timeout long et retries ; `server/gunicorn.conf.py` tient le worker à 120s.
- La qualité prime sur la cadence : un numéro pas au niveau du N°09 attend.
