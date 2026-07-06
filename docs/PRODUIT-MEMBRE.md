# PRODUIT MEMBRE · blueprint validé par panel adversaire
*Juillet 2026. Méthode : 4 visions produit incompatibles (atelier du digger,
chambre d'écoute, cabinet de curiosités, table d'écoute), chacune attaquée par
2 juges (abonné payant sceptique + analyste rétention), synthèse tranchée.
Complète docs/MONETISATION.md (l'offre et la mécanique restent inchangées) :
ce document définit le CONTENU membre et son niveau d'exigence.*

# BLUEPRINT FINAL · MEMBRE DU CIRCUIT
## CIRCUIT FERMÉ · juillet 2026

---

## 1. Le produit membre en une phrase

**Tu rachètes tes soirées de digging à une voix qui a déjà écouté les mauvais disques pour toi : chaque semaine quatre pièces racontées à la première personne, chaque mois un dossier de label introuvable ailleurs et un crate séquencé prêt à jouer, et un registre qui répond à tes requêtes.**

Ni PDF, ni prix Discogs recopiés, ni feuilleton. De l'utilité tangible (le haut de la hiérarchie du benchmark), portée par la seule chose que le produit possède en propre : la voix qui choisit.

---

## 2. Les cinq piliers

### Pilier 1 · Les pièces à la première personne (chaque numéro fermé)

**Quoi.** À partir du N°17, les 4 tracks scellées changent de registre : dehors la notice du critique, dedans le journal de première écoute. Provenance honnête et vécue (la face B écoutée par erreur cette semaine, le catalogue remonté depuis une pochette), jamais d'anecdote fabriquée, jamais d'horodatage fictif. Chaque champ `dig` porte en plus une ligne de fiche d'achat **evergreen** : « ↳ Viser le pressage X (CATNO). Éviter Y. » Sans prix, sans date.

**Pourquoi ça retient au mois 3.** C'est la seule feature qui rend la différence gratuit/membre **qualitative** et non quantitative : « la vraie réponse au verdict le texte seul ne vaut pas 5 € » (juge chambre 1), « structurellement inimitable, à condition que les provenances soient vécues » (juge chambre 2). La fiche d'achat amputée du daté est validée telle quelle : « evergreen, coûte réellement zéro, incarne la thèse du rachat d'heures » (juge atelier 2).

**Coût réaliste.** 0 min de texte en plus (consigne d'écriture sur du texte déjà budgété) + 2 min de fiche par numéro. La page release Discogs est déjà ouverte pour le fact-check bloquant.

**Pipeline.** Aucun changement : mêmes champs `body`/`dig`, seal standard `tools/circuit.py`. Une consigne ajoutée à `docs/PIPELINE-EDITORIAL.md`.

### Pilier 2 · Le Dossier (un label par mois, avec ses culs-de-sac)

**Quoi.** Une fois par mois, dans le premier numéro fermé du mois : la monographie d'un label du profil (satellites Wiggle, orbite KarateMusik, adjacents 20:20 Vision). 4 à 5 catnos dans l'ordre d'écoute, liens Discogs vérifiés, et la ligne la plus chère du produit : **les culs-de-sac signalés** (« les CATNO 12 à 18 sont la période trance, passe ton chemin »). Le label entre dans `track_history` : couvert à fond, gelé 10 éditions.

**Pourquoi ça retient au mois 3.** Verdict unanime des quatre juges qui l'ont vu. « La seule chose de la liste que ni First Floor, ni NTS, ni personne ne publie ; c'est le moat » (juge atelier 1). « La seule feature dont le wow survit au mois 3 sans entretien » (juge atelier 2). « LA raison pour laquelle je reste au mois 3, à condition de lui donner son vrai budget » (juge cabinet 1).

**Coût réaliste.** On assume l'attaque : **45 à 60 min**, une fois par mois, dans une session dédiée, pas dans les 30 min du numéro. C'est le seul poste lourd du produit, et il est mensuel. Les culs-de-sac exigent d'avoir vraiment préécouté les mauvais catnos : c'est précisément ce qu'on vend.

**Pipeline.** Bloc `section` à paragraphes dans `content/circuit/NN.json`, scellé par `--seal`, même mécanique que le label du mois public. Rythme mensuel = le gisement (25 à 30 labels dignes d'un arbre) dure 2 ans et plus, ce qui répond à l'attaque d'épuisement.

### Pilier 3 · Le crate calé et voté (dernier numéro fermé du mois)

**Quoi.** Le crate du mois existant monte d'un cran : ordre de lecture avec rôle par créneau (ouverture, palier, pivot electro, dernière heure) et note de transition d'une phrase (« sortir sur le break, la suivante entre à froid »). En amont, le premier fermé du mois propose trois directions (A/B/C), vote par lettre en réponse WhatsApp au message du code ; **on annonce la direction retenue, jamais le décompte** (l'attaque « 4 voix sur 13, plus embarrassant que pas de vote » est fondée). S'ajoute le registre du mois : une ligne sèche par pièce membre du mois (artiste · titre, label, catno, disponible Bandcamp / à chasser / écoute seule, lien).

**Pourquoi ça retient au mois 3.** « Byproduct réel du travail déjà budgété, il sert l'usage, le vendredi soir du membre, donc il vieillit bien et ne dépend d'aucun état de marché » (juge atelier 2). Le vote : « rendez-vous mensuel léger et sincère, qui crée une raison calendaire concrète de rester : revoir sa direction perdante au bulletin d'après » (juge table 1). Le registre du mois : « le seul anti-churn honnête du lot, son absence se sentirait physiquement en fin de mois » (juge atelier 1).

**Coût réaliste.** 10 min (transitions) + 5 min (directions et lecture des votes) + 10 min (registre du mois, métas déjà vérifiées) = **25 min par mois**, au-dessus du crate déjà budgété.

**Pipeline.** Tout est du texte dans les blocs membres existants, scellé par `--seal`. Le vote vit dans WhatsApp, connaître le code EST la preuve de membership, zéro infra.

### Pilier 4 · La requête au registre (quand ça matche, jamais promis)

**Quoi.** Le message mensuel du code invite à répondre par une demande libre (« plus dur que le N°18 », « la face B de ce monde-là »). Quand une requête croise le digging en cours ET passe toutes les règles (blocklist, no-repeat, fact-check, penchant electro), la track entre au registre créditée « Requête de M. 0NN ». Une par numéro maximum, zéro promise, zéro annoncée quand il n'y a rien. Chaque membre porte un numéro permanent à trois chiffres (M. 001...), cité dans les crédits ; **le total de membres n'est jamais publié** nulle part.

**Pourquoi ça retient au mois 3.** « La seule valeur d'usage introuvable chez First Floor ou NTS : un digging pointu qui te répond personnellement, avec un vrai filtre qualité derrière. C'est la raison n°1 de payer » (juge table 1). Le numéro de membre : « coût réel quasi nul, vrai objet de statut ; condition de survie : ne jamais publier le total » (juge table 2). Condition intégrée.

**Coût réaliste.** 0 à 5 min par numéro : la track sort du digging déjà en cours, le travail est de choisir la requête qui matche, pas de digger en plus. Pas de fenêtre, pas de SLA : les fenêtres restent des fenêtres.

**Pipeline.** Bloc track membre standard avec `position`, scellé normalement ; la ligne caviardée publique montre « Requête de M. 004 » sous barre noire : les non-membres voient que derrière le rideau, quelqu'un se fait servir. Liste des membres tenue hors git.

### Pilier 5 · Le recueil (le zine annuel reçoit sa définition)

**Quoi.** L'objet risographié déjà promis aux annuels devient le recueil de l'année du circuit : les 12 dossiers, les crates calés, les requêtes honorées avec leurs éditions, les pièces à la première personne. Maquette registre ivoire/noir/rouge : le design v5 est littéralement une riso deux couleurs. Chaque exemplaire numéroté à la main.

**Pourquoi ça retient au mois 3.** Gardé par les quatre juges qui l'ont vu, cas unique du dossier. « Zéro promesse nouvelle, zéro charge hebdomadaire, il rend le 50 €/an explicable en une phrase » (juge chambre 2). « Le seul endroit où la métaphore du registre devient un objet plutôt qu'un décor » (juge cabinet 1). « La seule feature dont le wow ne dépend pas d'une participation que 14 membres ne fourniront pas » (juge table 2).

**Coût réaliste.** 0 min par semaine. Une session de maquette en décembre via `circuit.py --open`. Seul risque résiduel : le coût d'impression sur ~93 € de marge mensuelle ; devis avant novembre.

**Pipeline.** Le contenu s'accumule seul dans les blobs chiffrés ; les TTF locales de `tools/assets/fonts/` servent l'export.

**Convention transverse à coût nul** : le lien magique `#c=` existant est cadré comme la place d'invité du membre (« Une place, une seule, à toi de choisir qui entre ce mois-ci ») : « la seule boucle d'acquisition du produit, la cascade de décaviardage comme démo exécutée par les membres » (juge table 2). Et les renvois entre pièces deviennent une convention d'écriture dans `dig`, **ouverts vers les pièces publiques aussi** (« le maillage sert la lecture, pas la strate », juge cabinet 1), jamais mis en avant dans le pitch tant que le pool est mince.

**Addition honnête.** Par numéro fermé : ~35 min (les 30 existantes + fiches + éventuelle requête). Par mois en plus : ~60 min de Dossier + ~25 min de crate calé. Total ~6 h/mois pour 6 à 8 numéros. Tenable, et rien ne dépend d'une donnée fraîche : une semaine sautée fait silence, pas promesse rompue.

---

## 3. Le N°17 · vendredi 24 juillet

**Ce que le public voit.**
- Tagline, ÉD. 017, cartouche PUBLIC.
- « Cette édition » : puces teasers non cliquables, dont une ligne annonçant le DOSSIER 01 sans nommer le label.
- Pièces 01/07 à 03/07 complètes : notice critique, méta structurée, ▶ Écouter + ↗ Bandcamp ou ◈ Discogs.
- La note de studio (publique, intacte : c'est l'appât).
- 1 stat à vraie donnée.
- Le registre caviardé : pièces 04/07 à 07/07 en lignes numérotées, année/format visibles, noms sous barre noire, tampon rouge RÉSERVÉ.
- Le verrou membre `#circuit-lock`, les deux Payment Links.

**Ce que le membre ouvre avec le code de juillet** (reçu dans la confirmation Stripe).
- **Pilier 1** : les pièces 04 à 07 au registre première personne, provenance vécue, fiche d'achat evergreen dans chaque `dig`.
- **Pilier 2** : DOSSIER 01, premier label monographié, 5 catnos ordonnés, culs-de-sac signalés, liens vérifiés. C'est la pièce maîtresse du lancement : le N°17 doit prouver le niveau N°09, pas le promettre.
- **Pilier 3 (amorce)** : les trois directions du crate de juillet (A/B/C), vote par réponse WhatsApp avant mercredi 29.
- **Pilier 4 (amorce)** : l'invitation à la requête, une phrase, sans promesse de délai.
- « Par où commencer », récap tracklist, mention du recueil pour les annuels, et le lien de passe du mois.

Seal obligatoire via `tools/circuit.py --seal` avant commit, jamais de clair membre dans git, notification FIFO au créneau du vendredi 10 h.

---

## 4. Roadmap jusqu'au 31 août

| Date | Livrable |
|---|---|
| **ven 24/07 · N°17** | Lancement fermé : piliers 1 et 2 pleins, amorces 3 et 4 (ci-dessus). Code de juillet généré, jamais commité. |
| **mar 28/07 · N°18** | Fermé standard : 3+4 en première personne, première requête servie si au niveau (sinon rien, sans annonce). |
| **ven 31/07 · N°19** | Dernier fermé de juillet : crate calé (direction gagnante, rôles, transitions), 3 tracks bonus avec notes de digging, registre du mois collable. |
| **sam 01/08** | Code d'août (`--gen-code`), message aux membres : code + lien de passe + rappel requête. Ouverture de l'Instagram anonyme, 1 post par numéro, rien d'autre. |
| **Août · N°20 à ~26** | Fenêtres mar/ven, pas quotas : ne fermer que ce qui est au niveau N°09. DOSSIER 02 dans le premier fermé d'août ; crate d'août calé et voté dans le dernier. |
| **Dès 5 membres** | Test Instagram 30 à 50 €, seuil d'arrêt 2 €/abonné, pas avant. |
| **~mi-août** | Point froid : membres, usage des codes, requêtes reçues. Aucune feature ajoutée avant le 31/08 : le produit se juge tel quel. |
| **lun 31/08** | Le seuil écrit reste inchangé : moins de 5 membres, le circuit rouvre, l'archive devient intégralement gratuite, et le portfolio garde un produit propre. Aucun seuil nouveau n'est ajouté. |

---

## 5. Ce qu'on tue et pourquoi

1. **Toute donnée de marché datée** (prix constatés, cotes, « pièce à saisir »). Sur des pages statiques non révocables, « l'archive fermée devient un cimetière de prix faux » et « la fraîcheur détruit son propre objet » (juges atelier 2 et cabinet 2) ; à 20 membres sur 4 copies, « les 18 autres trouvent le bac vide et c'est la déception qu'ils racontent ». La fiche d'achat survit uniquement amputée du daté.
2. **Le Registre général cumulatif, la numérotation d'inventaire à vie, le compteur public.** « L'archive gratuite avec des zéros de tête » (juge cabinet 1) ; le code qui ouvre tout l'inventaire fabrique l'abonnement intermittent, « payer 5 € un mois sur trois puis résilier : une machine à churn » (juge cabinet 2) ; et le compteur afficherait « 0 SCELLÉES » pendant les 5 semaines qui précèdent le seuil.
3. **Le sentier** (recettes de digging). « Vous m'avez vendu la canne qui rend le poisson inutile » (juge atelier 1) : de la valeur one-shot déguisée en abonnement.
4. **La pièce refusée.** « Par définition je paie pour la track jugée pas assez bonne », elle gèle du no-repeat, et « au 6e numéro on fabrique des refus pour nourrir la rubrique » (juges chambre 1 et 2).
5. **La traversée en feuilleton.** « Un feuilleton troué déçoit plus qu'aucun feuilleton » (juge chambre 2), et la cartographie de scène existe gratuitement ailleurs. Le Dossier mensuel autoporté fait le même travail sans dette de chapitres.
6. **Le courrier du circuit.** À moins de 20 membres, le fallback est « une auto-interview mensuelle déguisée qui sonne creux » (juge chambre 2). La requête au registre fait mieux : elle répond en musique, pas en prose.
7. **La pièce versée.** Le veto quasi systématique produit une phrase publique « rien n'a passé » : « une humiliation douce répétée, pas de la rétention » (juge table 2).
8. **Le total de membres publié et tout décompte de vote.** « Le dispositif de statut se retourne en compteur de bar qui se vide » (juge table 2). On publie des numéros de membres et des directions gagnantes, jamais des effectifs.
9. **La contre-note hebdomadaire et les horodatages fictifs.** « Il n'existe pas 4 récits intimes par semaine ; une anecdote fausse repérée par un proche tue la moat entière » (juge chambre 2), et la contre-note « converge vers 3 tropes au bout de 6 numéros ». La voix intime vit dans les pièces à la première personne, un seul registre, honnête, chaque semaine ; on n'assèche pas deux puits à la fois.

Le principe qui a tout arbitré : rien dans l'offre membre ne périme, rien ne dépend d'une participation que 14 personnes ne fourniront pas, rien ne promet un rythme que 30 minutes par session ne tiennent pas. Quatre pièces vécues par semaine, un dossier et un crate par mois, un objet par an. C'est court, c'est tenable, et chaque ligne est introuvable ailleurs.

---

## 6. Doctrine de clarté et conventions premium

*Verdict d'Adam sur le premier spécimen membre (juillet 2026) : « pas clair du
tout, tout doit être crystal clear ». Ces conventions sont obligatoires sur
tout numéro fermé. La clarté s'ajoute AUTOUR de la prose, elle ne la dilue
pas : le niveau d'écriture des pièces reste celui des piliers.*

1. **Chaque dispositif s'auto-explique à la première rencontre, en une
   ligne.** Un lecteur qui débarque ne connaît ni « M. 004 », ni « requête »,
   ni « dossier », ni « crate ». Conventions fixées :
   - **La requête** : sa section porte le chapeau « La requête du mois : un
     membre demande, la sélection répond », et la pièce ouvre sur « M. 004
     (chaque membre porte un numéro) a demandé : ... Voici la réponse. »
   - **Le dossier** : chapeau « Le dossier, chaque mois : un label passé au
     crible, ce qu'il faut écouter, dans quel ordre, et ce qu'il faut
     éviter. »
   - **Le crate** : chapeau « Le crate du mois : votre sélection du mois,
     ordonnée pour être jouée telle quelle, du premier au dernier disque. »
   - **La fiche d'achat** : étiquetée dans `dig`, jamais un ↳ nu :
     « FICHE D'ACHAT · Acheter : ... Éviter : ... »
2. **Chaque texte commence par sa thèse**, note de studio comprise : la
   première phrase annonce de quoi le texte parle, puis il déroule. Jamais
   d'ouverture en énigme. Un lecteur pressé doit comprendre chaque paragraphe
   isolément.
3. **Phrases courtes, un fait par phrase, aucune référence interne non
   expliquée** : pas de « direction B » sans dire qu'un vote a eu lieu, pas
   de numéro de membre sans dire que chaque membre en porte un.
4. **Le chapeau membre** ouvre la zone membre : « Registre complet · vous
   lisez la version membre », plus une ligne qui liste ce que CE numéro
   contient pour le membre (pièces racontées, dossier, crate, requête).
5. **Le reçu de fin de mois** ferme la zone membre : « Votre mois de X en
   tant que membre : N pièces racontées et sourcées · 1 label passé au
   crible · 1 crate prêt à jouer · 1 requête servie. » La preuve de valeur,
   factuelle, sans emphase.
6. **Chaque section membre porte une raison d'être d'une ligne** (pourquoi ce
   contenu vaut l'abonnement), intégrée naturellement au chapeau ou au titre
   de section, jamais en argumentaire lourd.
