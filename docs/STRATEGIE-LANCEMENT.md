# STRATÉGIE DE LANCEMENT · CIRCUIT FERMÉ

Départ : samedi 4 juillet 2026 au soir. Objectif du mois : 20 abonnés push
actifs, la mécanique du club installée, le membership (5 €/mois ou 50 €/an)
activé fin juillet. Tout ce qui est marqué AUTO tourne sans intervention.

## Semaine 0 · l'amorce

- **Ven 3 juillet, 10h** (AUTO) : notif N°11 « Londres ne dormait pas ».
  Adam doit être abonné AVANT (ouvrir le site, S'abonner, vérifier réception).
- **Sam 4 juillet, soir · LANCEMENT** : partage personnel du lien
  https://arochab.github.io/kapman-news/ dans le cercle proche (WhatsApp
  perso, pas les canaux Escape : la marque reste séparée). Message type :
  « je lance un truc, 2 sélections par semaine, zéro algo, abonne-toi en
  un tap ». Objectif : 10 abonnés avant dimanche soir. Le QR du site sert
  en soirée si l'occasion se présente.
- **Dim 5 juillet** : relance douce des non-abonnés (1 message max).

## Semaine 1 · la cadence s'installe

- **Mar 7, 10h** (AUTO) : N°12 « Le dub comme méthode » rendu, publié, envoyé.
- **Mar 7, 10h45** (AUTO) : squelette N°13 créé.
- **Mer 8** : session d'écriture N°13 (penchant ELECTRO, cf CLAUDE.md).
  30 min de session Claude suffisent : le pipeline fait le reste.
- **Ven 10, 10h** (AUTO) : N°13 part.
- **Week-end 11-12** : demander à 3 abonnés ce qu'ils ont écouté / gardé.
  C'est le premier signal produit réel.

## Semaine 2 · la cabine

- **Mar 14, 10h** (AUTO) : N°14 (à écrire lun 13).
- **Mer 15** : ouverture de « la cabine », group chat WhatsApp privé des
  abonnés (invitation dans le N°15 + message perso). Zéro outil à payer.
  Elle reste gratuite et ouverte, avant comme après l'ouverture du circuit.
- **Ven 17, 10h** (AUTO) : N°15, avec une ligne d'annonce : la cabine ouverte.

## Semaine 3 · l'argent

- **Lun 20** : compte Stripe + 2 Payment Links (5 €/mois, 50 €/an) + portail
  client (~20 min, guide docs/MONETISATION.md). Le message de confirmation
  post-achat est configuré avec le code du circuit de juillet, généré via
  `python tools/circuit.py --gen-code` et noté par Adam. URLs dans
  content/site.json, rebuild, push [skip notify] : le bloc « Membre du
  circuit » apparaît sur tout le site.
- **Mar 21, 10h** (AUTO) : N°16, avec UNE ligne de teaser : « vendredi, le
  circuit se ferme ».
- **Ven 24, 10h** (AUTO) : N°17 · premier numéro fermé, avec l'annonce
  complète du modèle (texte prêt à coller dans docs/MONETISATION.md).

## Semaine 4 · le bilan

- **Mar 28, 10h** (AUTO) : N°18 fermé (à écrire lun 27).
- **Ven 31, 10h** (AUTO) : N°19 fermé, avec le crate de juillet dans le
  circuit (playlist du mois + 3 tracks bonus, cf docs/MONETISATION.md).
- **Bilan chiffré fin de mois** : abonnés push (via GET / du serveur),
  membres Stripe. Seuil de décision au 31 août 2026 : cf
  docs/MONETISATION.md.

## Rappels permanents

- Les créneaux sont des fenêtres, pas des quotas : un numéro pas prêt glisse.
- Écriture d'un numéro : 1 session courte, sélection hors playlists
  (blocklist), electro d'abord, liens vérifiés, zéro tiret.
- Le marketing = le bouche à oreille + le QR + le circuit. Pas de réseaux
  publics tant que l'anonymat KAPMAN compte.

## La comm · less is more, le produit parle

Principe : zéro communication qui ne soit pas le produit lui-même. Chaque
numéro public (3 tracks fortes + design) EST l'asset de comm ; on ne crée
jamais de contenu marketing séparé.
- **Le partage fait le marketing** : chaque page doit être belle à partager.
  Action (mi-juillet, session courte) : balises OG + image de partage par
  numéro générée au build (tagline + triple-rule + 3 tracks, direction
  artistique du site). Quiconque colle le lien dans WhatsApp/iMessage/
  Instagram diffuse la marque toute seule.
- **Un seul réseau, tenu** : un compte Instagram CIRCUIT FERMÉ, anonyme
  (l'anonymat d'Adam est préservé : la marque vit seule, le crédit footer
  suffit). Ouverture ~1er août, après un mois d'archive publique. Cadence
  calée sur la lettre : 1 post par numéro (l'image de partage) + 1 story
  avec lien. Rien d'autre. Pas de reels forcés, pas de présence
  multi-plateformes.
- **Les liens magiques comme munition** : pour chaque relais pressenti
  (DJ, compte de scène), un lien magique d'UN numéro en message privé,
  personnel, jamais de mass DM.
- **Sponsoring : après la preuve, pas avant.** Aucun euro de pub avant le
  seuil des 5 membres (31 août). Ensuite : test unique de 30 à 50 € de
  boost Instagram sur le post d'un numéro fort, ciblage Paris + intérêts
  scène (clubs, labels, festivals pointus), mesuré en abonnés push gagnés.
  On ne renouvelle que si le coût par abonné est inférieur à 2 €.
- **Jalon** : à 100 abonnés push, réévaluer (2e canal éventuel, presse
  spécialisée, partenariat lieu). Avant ça, la seule stratégie est la
  régularité et la qualité des numéros publics.
