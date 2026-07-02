# Monétisation — abonnement de soutien (5 €/mois)

KAPMAN SIGNAL est un projet gratuit et open source. Ce document décrit la
brique d'abonnement de soutien : un moyen simple pour les lecteurs qui le
souhaitent de financer la suite (sélection, serveur, archives), sans jamais
restreindre l'accès au contenu.

Tant que `content/site.json` → `membership_url` est vide, **rien n'apparaît**
sur le site (ni sur les issues, ni sur la home). Le bloc est purement additif.

## Mise en place (côté Adam)

1. **Créer le compte Stripe** — [stripe.com](https://stripe.com). Il faut une
   pièce d'identité et un IBAN pour recevoir les paiements. Compter ~10 min.

2. **Créer le produit** — dans le dashboard Stripe : *Produits* → *Ajouter un
   produit*.
   - Nom : `KAPMAN SIGNAL — Abonnement de soutien`
   - Prix : récurrent, mensuel, **5,00 € EUR**

3. **Créer un Payment Link** pour ce prix (*Paiements* → *Liens de paiement*,
   ou directement depuis la fiche produit).
   - Activer le **portail client** (« customer portal ») pour que les
     abonnés puissent résilier en autonomie, sans avoir à écrire à qui que
     ce soit.
   - Optionnel : rendre le champ e-mail obligatoire (utile pour le suivi et
     pour dire merci ponctuellement).

4. **Configurer le site** — coller l'URL du Payment Link dans
   `content/site.json` :

   ```json
   {
     "membership_url": "https://buy.stripe.com/xxxxxxxxxxxx",
     "membership_price": "5 € / mois"
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
   git commit -m "Active l'abonnement de soutien [skip notify]"
   git push
   ```

   Le bloc « Abonnement de soutien » apparaît alors sur toutes les issues
   déjà publiées et sur la home.

6. **Suivi des abonnés** — tout se passe dans le dashboard Stripe (nombre
   d'abonnés, paiements, désabonnements/churn). Les e-mails collectés à
   l'étape 3 permettent d'envoyer un merci ponctuel aux soutiens, mais ne
   sont pas utilisés pour la diffusion de la newsletter elle-même (ça reste
   le rôle du push).

## Limites & suite

- Le dépôt GitHub est **public** : le contenu de chaque issue reste lisible
  par n'importe qui, abonné ou non. Ce n'est **pas un paywall** — c'est un
  abonnement de soutien volontaire, un geste. C'est un choix assumé, cohérent
  avec l'esprit « portfolio + petit cercle d'amis » du projet.
- Pour un vrai paywall (v3, si le besoin se présente un jour) il faudrait
  changer d'architecture : dépôt privé + hébergement avec authentification
  (par ex. Render avec check de session, ou Cloudflare Access devant les
  pages), ou bien migrer vers une plateforme dédiée à l'abonnement payant.
  À décider plus tard, pas urgent.
- Alternatives à Stripe si jamais : **Ko-fi** ou **Liberapay** — moins
  « pro » dans le rendu, mais zéro friction à mettre en place (pas de KYC
  aussi lourd, pages hébergées prêtes à l'emploi). Stripe reste préférable
  ici pour le rendu et le portail client en self-service.
