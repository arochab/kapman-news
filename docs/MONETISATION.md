# Monétisation · Membre du circuit

Principe : la lettre CIRCUIT FERMÉ reste 100 % gratuite et publique (canal
d'acquisition). On vend l'appartenance, pas le texte : un paywall convertirait
3 à 10 %, soit 1 à 3 payants sur le lectorat actuel (cf docs/AUDIT-EDITORIAL.md).
Framing public type NTS : « le contenu reste ouvert, tu finances la suite ».

## L'offre

Deux paliers, deux Payment Links Stripe :

- **5 €/mois** (mensuel)
- **50 €/an** (2 mois offerts + le totem de fin d'année)

Ce que le membre débloque :

1. **La Séance** (le cœur) : écoute collective mensuelle au lieu ami, la
   sélection du mois jouée en entier, lumière basse, débrief. Séance #1 le
   samedi 25 juillet 2026, gratuite pour tous (produit d'appel et moment de
   conversion) ; ensuite réservée aux membres sur RSVP. Jamais d'argent sur
   place.
2. **Le crate du mois** (l'utilité) : la playlist prête à jouer des numéros
   du mois + 3 tracks bonus hors flux public avec notes de digging. Rédigé
   dans la même session que le dernier numéro du mois (coût marginal quasi
   nul). Mêmes règles éditoriales que la lettre (blocklist des playlists
   d'Adam, no repeat 10 éditions, liens vérifiés). Livré le dernier vendredi
   du mois en message privé WhatsApp aux membres (liste tirée du dashboard
   Stripe ; trivial sous 20 membres).
3. **La cabine** : le group chat WhatsApp reste GRATUIT et ouvert à tous les
   abonnés (canal d'acquisition, pas un perk). Le perk membre, c'est le crate
   en privé et la Séance.
4. **Le totem annuel** (l'objet) : zine risographié réservé au palier annuel,
   tirage 50 à 100 exemplaires, expédié en décembre. (Ne jamais promettre de
   K7 publiquement ; ça reste un bonus interne éventuel.)

## Économie

20 membres = 100 €/mois (net Stripe ~93 €) : la Séance et le zine
s'autofinancent. À cette échelle c'est un club qui se finance, pas un
salaire ; le revenu viendra de la taille. Note non bloquante : des revenus
récurrents se déclarent (micro-BNC) · décision d'Adam.

## Seuil de décision (écrit d'avance)

Moins de 5 membres au 31 août 2026 : le club redevient gratuit, on retente à
50+ abonnés push. 5 ou plus : rituel confirmé, Séance mensuelle et crate
pérennisés.

## Annonce N°17 (prête à coller, verbatim)

> Le circuit s'ouvre. La lettre reste gratuite, rien ne change ici. Les
> membres (5 € par mois ou 50 € l'année) financent la suite : la Séance
> d'écoute mensuelle, le crate du mois avec ses tracks bonus, et l'objet de
> fin d'année pour les annuels. Première Séance demain soir.

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
   - Rendre le champ e-mail obligatoire (utile pour le suivi du crate et
     pour dire merci ponctuellement).

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
   d'abonnés, paiements, désabonnements/churn, e-mails collectés pour le
   crate du mois et les mercis ponctuels).

## Distribution du crate

Liste des membres tirée du dashboard Stripe → message privé WhatsApp le
dernier vendredi du mois. Pas de nouvel outil tant qu'on est sous 20
membres.

## Limites & suite

- Le dépôt GitHub est **public** : le contenu de chaque issue reste lisible
  par n'importe qui, membre ou non. Ce n'est **pas un paywall**, c'est de
  l'appartenance volontaire. Choix assumé, cohérent avec l'esprit
  « portfolio + petit cercle d'amis » du projet.
- Pour un vrai paywall (v3 hypothétique, si le besoin se présente un jour)
  il faudrait changer d'architecture : dépôt privé + hébergement avec
  authentification (par ex. Render avec check de session, ou Cloudflare
  Access devant les pages), ou bien migrer vers une plateforme dédiée à
  l'abonnement payant. À décider plus tard, pas urgent.
- Alternatives à Stripe si jamais : **Ko-fi** ou **Liberapay**, moins
  « pro » dans le rendu mais zéro friction à mettre en place (pas de KYC
  aussi lourd, pages hébergées prêtes à l'emploi). Stripe reste préférable
  ici pour le rendu et le portail client en self-service.
