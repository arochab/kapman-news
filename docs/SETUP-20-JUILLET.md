# Setup du lundi 20 juillet · checklist (~30 min)

Pré-requis déjà en poche : micro-entreprise ACTIVE (immatriculée 2023, espace
pro DGFiP et compte URSSAF ouverts). Le SIREN est dans les mails DGFiP
(recherche Gmail : « DGFIP dossier fiscal », mail du 28/09/2023). Ne jamais
l'écrire dans ce repo.

1. Revolut : copier l'IBAN EUR (onglet Comptes).
2. stripe.com : créer le compte, profil « entreprise individuelle », SIREN,
   activité « newsletter musicale par abonnement ». Identité : pièce + selfie.
3. Compte de versement : coller l'IBAN Revolut. Versements automatiques,
   sans frais.
4. Produits : « Membre du circuit · mensuel » 5,00 € récurrent mensuel et
   « Membre du circuit · annuel » 50,00 € récurrent annuel. Un Payment Link
   par produit. Activer le portail client (résiliation en autonomie) et
   l'e-mail obligatoire.
5. Dans chaque Payment Link, message de confirmation post-achat : le code du
   circuit du mois (générer avec `python tools/circuit.py --gen-code`, le
   noter dans un endroit sûr HORS repo) + « garde ce code, il ouvre les
   numéros du mois ».
6. Coller les 2 URLs dans content/site.json (membership_url,
   membership_annual_url), `python tools/build_issue.py --rebuild-all`,
   commit `[skip notify]`, push.
7. Rappels : déclarer les encaissements dans la déclaration URSSAF
   habituelle (~21 à 26 %) ; frais Stripe ~1,5 % + 0,25 €/paiement ;
   vérifier un jour que le libellé d'activité INPI couvre un service
   d'abonnement en ligne (non bloquant) ; facturation électronique
   obligatoire au 01/09/2026, désigner une plateforme gratuite le moment
   venu (mail DGFiP de juin 2026).
