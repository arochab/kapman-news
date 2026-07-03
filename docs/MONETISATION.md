# Monétisation · Membre du circuit

Principe : freemium. La version publique de chaque numéro reste digne de la
marque (c'est le canal d'acquisition) ; la version complète vit dans « le
circuit » (les membres). Prix : 5 €/mois ou 50 €/an (2 mois offerts + l'objet
de fin d'année, un zine risographié : jamais promettre de K7). Deux Payment
Links Stripe, un par palier.

## Le découpage éditorial

À respecter à chaque numéro fermé (à partir du N°17) :

**Gratuit** (page publique) :
- la tagline
- les puces « Cette édition » (celles qui renvoient à des sections fermées
  deviennent des teasers non cliquables)
- 3 tracks sur 7, avec textes et liens complets
- la note de studio
- 1 stat

**Circuit** (déverrouillé par le code du mois) :
- les 4 autres tracks
- « Par où commencer »
- le récap tracklist complet
- le crate du mois, dans le dernier numéro du mois : la playlist prête à
  jouer + 3 tracks bonus avec notes de digging (mêmes règles éditoriales que
  la lettre : blocklist des playlists d'Adam, no repeat 10 éditions, liens
  vérifiés)
- l'archive des numéros fermés

Les numéros 09 à 16 restent complets et gratuits : c'est l'archive d'appel.
Le circuit se ferme au N°17 (vendredi 24 juillet 2026), en même temps que
l'activation Stripe.

## Le code du circuit

Un code par mois, format trois mots plus deux chiffres, généré par
`python tools/circuit.py --gen-code`. Le code n'est jamais commité ni publié
sur le site : il est distribué via le message de confirmation post-achat
Stripe (configurable dans le Payment Link) et rappelé en privé.

Un membre qui résilie perd les codes suivants et garde les anciens (les
numéros déjà déverrouillés restent lisibles chez lui, rien à révoquer côté
serveur puisque tout est statique).

Limite assumée : un code peut se partager. La rotation mensuelle et le petit
cercle suffisent : on ne vend pas des secrets d'État, on vend l'appartenance
et le geste.

## Mise en place Stripe (lun 20 juillet, ~20 min)

1. **Créer le compte Stripe** · [stripe.com](https://stripe.com). Il faut
   une pièce d'identité et un IBAN pour recevoir les paiements. Compter ~10
   min.

2. **Créer les deux produits** · dans le dashboard Stripe : *Produits* →
   *Ajouter un produit*.
   - « Membre du circuit · mensuel », prix récurrent mensuel, **5,00 € EUR**.
   - « Membre du circuit · annuel », prix récurrent annuel, **50,00 € EUR**.

3. **Créer un Payment Link par produit** (*Paiements* → *Liens de paiement*,
   ou directement depuis chaque fiche produit).
   - Activer le **portail client** (« customer portal ») pour que les
     membres puissent résilier en autonomie, sans avoir à écrire à qui que
     ce soit.
   - Rendre le champ e-mail obligatoire (utile pour le suivi et pour dire
     merci ponctuellement).
   - Configurer le **message de confirmation post-achat** pour qu'il
     contienne le code du circuit du mois en cours et le lien WhatsApp de la
     cabine.

4. **Configurer le site** · coller les deux URLs dans `content/site.json` :

   ```json
   {
     "membership_url": "https://buy.stripe.com/xxxxxxxxxxxx",
     "membership_price": "5 € / mois",
     "membership_annual_url": "https://buy.stripe.com/yyyyyyyyyyyy",
     "membership_annual_price": "50 € / an"
   }
   ```

5. **Rebuild + publier** :

   ```
   python tools/build_issue.py --rebuild-all
   ```

   Puis commit + push, en incluant `[skip notify]` dans le message de commit
   pour ne pas déclencher une notification push (ce n'est pas une nouvelle
   issue) :

   ```
   git add content/site.json issues/ index.html
   git commit -m "Active le membership du circuit [skip notify]"
   git push
   ```

   Tant que `membership_url` est vide, **rien ne s'affiche** sur le site (le
   bloc est purement additif). Une fois rempli, le bloc « Membre du circuit »
   apparaît sur toutes les issues déjà publiées et sur la home.

6. **Suivi des membres** · tout se passe dans le dashboard Stripe (nombre
   d'abonnés, paiements, désabonnements/churn, e-mails collectés).

## Économie

20 membres = 100 €/mois (net Stripe ~93 €) : le zine et le projet
s'autofinancent. À cette échelle c'est un club qui se finance, pas un
salaire. Note non bloquante : des revenus récurrents se déclarent
(micro-BNC), décision d'Adam.

## Seuil de décision (écrit d'avance)

Moins de 5 membres au 31 août 2026 : le circuit rouvre (tout redevient
gratuit), on retente à 50+ abonnés push. 5 membres ou plus : modèle
confirmé.

## Annonce N°17 (prête à coller, verbatim)

> Le circuit se ferme. À partir de ce numéro, la lettre publique garde trois
> tracks et la note de studio. Le reste (quatre tracks, par où commencer, le
> crate du mois) vit dans le circuit : 5 € par mois ou 50 € l'année, le code
> arrive à l'inscription. Rien d'autre ne change.

## Accès offerts (testeurs et relais)

Le lien magique rend tout accès offert trivial : une URL de numéro avec le
code en fragment (`…/issues/17/#c=<code du mois>`) déverrouille au premier
clic, sans saisie ; le fragment ne quitte jamais le navigateur et l'URL se
nettoie toute seule.
- **Cercle testeurs** (5 à 10 très proches) : le code du mois offert, envoyé
  chaque mois en privé. Leur paiement, c'est le retour d'usage.
- **Relais** (DJs, comptes de la scène, presse) : un lien magique vers UN
  numéro précis, jamais l'archive. Le code tournant limite la casse si le
  lien fuit.
- Quand ça prendra de la hauteur : passer aux codes multiples par numéro
  (clé de contenu enveloppée sous plusieurs codes : membre, invité,
  campagne, révocables séparément). Noté comme évolution v2 de
  tools/circuit.py, pas urgent.

## Idées pour plus tard

- La Séance d'écoute collective : reportée, trop tôt.
- La cabine WhatsApp reste gratuite et ouverte.
