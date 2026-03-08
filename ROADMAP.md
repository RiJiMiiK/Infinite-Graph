# Roadmap

Cette roadmap decrit l'etat actuel du projet `Infinite Graph`, ce qui a deja ete fait, et les prochaines etapes possibles.

## 1. Fondations du projet

- [x] Depot Git initialise
- [x] Projet pousse sur GitHub
- [x] Structure Python propre avec point d'entree dans `main.py`
- [x] Code separe dans `src/infinite_graph`
- [x] Dependances centralisees dans `requirements.txt`
- [x] Documentation de base dans `README.md`
- [x] Ajouter une licence si necessaire
- [x] Clarifier la vision produit dans le `README`
- [x] Ajouter un changelog si le projet grossit

## 2. Chargement et validation des saves

- [x] Support du vrai format Infinite Craft avec `items`
- [x] Support d'un format JSON simplifie de test
- [x] Extraction normalisee des recettes sous forme `left`, `right`, `result`
- [x] Validation des starters obligatoires `Water`, `Fire`, `Wind`, `Earth`
- [x] Erreur explicite si un starter est manquant
- [x] Mieux gerer les saves partiellement corrompues
- [x] Signaler les recettes invalides ignorees
- [x] Ajouter des tests unitaires de parsing

## 3. Modele du graphe

- [x] Chaque element est un noeud
- [x] Chaque recette `A + B = C` cree jusqu'a deux edges : `A -> C` et `B -> C`
- [x] Fusion des edges deja existantes
- [x] Conservation de la liste des co-elements sur chaque edge
- [x] Poids d'une edge = `len(liste_des_co-elements)`
- [x] Calcul du poids minimal des noeuds
- [x] Poids `0` pour les starters
- [x] Poids d'un resultat = `poids(A) + poids(B) + 1`
- [x] Conservation du poids minimal si plusieurs recettes produisent le meme resultat
- [x] Propagation amelioree avec priorite aux plus petits poids
- [x] Ajouter des tests unitaires sur le calcul des poids
- [x] Ajouter des tests sur la fusion des edges
- [x] Ajouter des tests de regression sur des mini-saves

## 4. Interface graphique

- [x] GUI desktop en Qt
- [x] Onglet `Graphe`
- [x] Onglet `Infos`
- [x] Onglet `Statistiques`
- [x] Rendu natif du graphe avec `pyqtgraph`
- [x] Layout actuel base sur `spring layout`
- [x] Zoom et deplacement dans la vue graphe
- [x] Tableau des noeuds avec leur poids
- [x] Tableau des edges avec leur poids et leurs co-elements
- [x] Graphique du nombre de recettes faites par poids du resultat
- [x] Graphique du nombre d'elements par poids
- [x] Liste du nombre de recettes non faites possibles par poids
- [x] Selection d'un noeud dans le graphe
- [ ] Mise en surbrillance de ses voisins
- [ ] Panneau d'informations pour le noeud selectionne
- [ ] Recherche d'un element dans la vue
- [ ] Centrage automatique sur un element
- [ ] Filtrage du graphe par sous-graphe
- [ ] Filtrage par poids minimal / maximal
- [ ] Reglages de layout via l'interface

## 5. Experience utilisateur pendant la generation

- [x] Generation executee hors du thread principal
- [x] Fenetre qui reste responsive pendant le traitement
- [x] Barre de progression indeterminee
- [x] Affichage de l'etape courante
- [x] Progression detaillee pendant le `spring layout`
- [x] ETA approximative pendant le calcul du layout
- [ ] Vraie barre de progression en pourcentage
- [ ] Etapes encore plus fines
- [ ] Temps total de generation affiche
- [ ] Cache local du layout pour eviter de tout recalculer

## 6. Gestion des combinaisons candidates

- [x] Deux champs `Element 1` et `Element 2`
- [x] Bouton `Random`
- [x] Bouton `Cheapest`
- [x] Bouton `Done`
- [x] Bouton `Discard`
- [x] `Random` propose une combinaison non faite aleatoire
- [x] `Cheapest` propose une combinaison avec le poids de resultat minimal
- [x] `Done` marque la combinaison comme faite pour la session courante uniquement
- [x] `Discard` marque la combinaison comme impossible de facon persistante
- [x] `Random` et `Cheapest` excluent les recettes connues
- [x] `Random` et `Cheapest` excluent les combinaisons discardees
- [x] `Random` et `Cheapest` excluent les combinaisons marquees `done` dans la session
- [x] Les champs sont editables
- [x] Un clic sur un champ copie son contenu dans le presse-papiers
- [x] Les champs sont vides apres `Done`
- [x] Les champs sont vides apres `Discard`
- [x] Pas de pop-up pour `Done`
- [ ] Auto-completion des noms d'elements
- [ ] Bouton `Undo Done`
- [ ] Bouton `Undo Discard`
- [ ] Bouton pour passer directement a la suggestion suivante
- [ ] Historique local des dernieres suggestions
- [ ] Validation en direct des noms saisis

## 7. Persistance locale

- [x] Fichier global `discarded.json`
- [x] Combinaisons discardees globales, independantes de la save
- [x] Compatibilite avec l'ancien format de `discarded.json`
- [x] Reecriture au nouveau format global
- [ ] Interface pour consulter les combinaisons discardees
- [ ] Suppression manuelle d'une combinaison discardee
- [ ] Reset complet du fichier `discarded.json`
- [ ] Export / import manuel si besoin

## 8. Nettoyage deja effectue

- [x] Suppression du CLI
- [x] Suppression du rendu HTML
- [x] Suppression des assets web inutiles
- [x] Suppression de l'export CSV
- [x] Nettoyage de la documentation en consequence
- [ ] Nettoyer `.gitignore` si certains ignores ne servent plus
- [ ] Verifier s'il reste des fichiers morts dans le repo

## 9. Qualite logicielle

- [x] Tests unitaires sur le chargement des saves
- [x] Tests unitaires sur la validation des starters
- [x] Tests unitaires sur le calcul des poids
- [x] Tests unitaires sur la fusion des edges
- [x] Tests unitaires sur `Random`
- [x] Tests unitaires sur `Cheapest`
- [x] Tests unitaires sur `Done`
- [x] Tests unitaires sur `Discard`
- [x] Tests de persistance sur `discarded.json`
- [x] Tests GUI minimaux
- [x] Ajout d'un formatter
- [x] Ajout d'un linter
- [ ] Ajout d'une CI GitHub Actions

## 10. Performance

- [x] Traitement lourd sorti du thread principal
- [x] Etat courant du traitement visible par l'utilisateur
- [ ] Optimiser le `spring layout`
- [ ] Mettre en cache les positions des noeuds
- [ ] Eviter un recalcul complet si seule l'interface change
- [ ] Calculer des sous-graphes au lieu du graphe complet si necessaire
- [ ] Indexer plus efficacement les combinaisons candidates

## 11. UX produit

- [ ] Indiquer pourquoi une combinaison n'est plus proposee
- [ ] Ajouter un panneau `current candidate`
- [ ] Proposer plusieurs `Cheapest` au lieu d'une seule
- [ ] Proposer plusieurs `Random`
- [ ] Afficher un compteur de combinaisons candidates restantes

## 12. Priorites recommandees

### Priorite haute

- [ ] Auto-completion pour `Element 1` et `Element 2`
- [ ] `Undo Done`
- [ ] `Undo Discard`
- [ ] Selection d'un noeud dans le graphe avec details

### Priorite moyenne

- [ ] Cache du `spring layout`
- [ ] Recherche d'un element
- [ ] Centrage sur un element
- [ ] Sous-graphe autour d'un element

### Priorite basse

- [ ] Tests GUI plus pousses
- [ ] Outils de gestion du fichier `discarded.json`
- [ ] Meilleure presentation du graphe pour les tres gros jeux de donnees
