# Infinite Graph

Outil desktop Python pour analyser une sauvegarde d'Infinite Craft, visualiser son graphe, et piloter les combinaisons encore candidates.

## Vision

Infinite Graph a pour but de servir d'outil d'exploration pour une sauvegarde Infinite Craft.

L'idee n'est pas seulement d'afficher un graphe, mais de :

- comprendre la structure des elements deja decouverts
- estimer leur profondeur via un poids minimal
- identifier rapidement des combinaisons encore non tentees
- suivre localement les combinaisons deja essayees ou jugees inutiles

Le projet est pense comme un outil desktop interactif, centre sur l'analyse et la prise de decision, plutot qu'un simple export statique.

## Fonctionnalites

- lecture d'une sauvegarde Infinite Craft reelle ou d'un format JSON simplifie
- interface graphique Qt complete
- graphe natif avec `pyqtgraph`, zoom, deplacement, selection de noeud et mise en surbrillance des voisins
- theme global sombre, avec vue graphe egalement en dark mode
- calcul du poids minimal des noeuds et fusion des edges
- suggestions de combinaisons avec `Random`, `Cheapest`, `Next`, `Done`, `Discard`, `Undo Done`, `Undo Discard`
- historique local des dernieres suggestions
- panneau `current candidate` avec statut, origine, poids estime et compteur restant
- gestion globale des combinaisons ignorees via `discarded.json`
- import, export, reset et consultation des `discarded`
- statistiques sur les poids des recettes, noeuds et combinaisons candidates
- generation asynchrone avec progression detaillee, temps total et cache local du layout
- sous-graphe, filtre par poids et reglages de layout dans l'onglet graphe

## Formats supportes

Le projet supporte maintenant :

- une vraie sauvegarde Infinite Craft avec une cle `items`
- un format JSON simplifie de test

Exemple du format simplifie :

```json
{
  "elements": ["Water", "Fire", "Steam"],
  "recipes": [
    { "left": "Water", "right": "Fire", "result": "Steam" }
  ]
}
```

Il accepte aussi des variantes de cles :

- `left` / `right` / `result`
- `first` / `second` / `result`
- `a` / `b` / `result`

Pour les elements, chaque entree peut etre une chaine ou un objet avec `name`, `text` ou `result`.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Conventions de code

Le projet suit explicitement :

- `PEP 8` pour le style Python general
- `PEP 257` pour les conventions de docstrings
- `PEP 20` pour les principes de lisibilite et de conception

Outils actuellement utilises dans le repo :

- `black` pour le formatage
- `isort` pour les imports
- `pylint` pour les checks statiques

Politique de taille des modules :

- alerte a partir de `800` lignes
- echec a partir de `1000` lignes

Cette regle est une convention interne du projet inspiree par les objectifs de maintenabilite, modularite et analysabilite.

CI actuelle :

- GitHub Actions execute `pytest --cov --cov-report=term-missing`
- GitHub Actions execute `pylint main.py src`

## Utilisation GUI

```bash
python main.py
```

## Fichiers du projet

- `ROADMAP.md` : roadmap detaillee
- `CHANGELOG.md` : historique des evolutions
- `discarded.json` : combinaisons globalement ignorees
- `LICENSE` : licence du projet

Dans l'interface :

- choisis le fichier de sauvegarde
- clique sur `Generer`
- utilise `Random`, `Cheapest` et `Next` pour faire tourner les suggestions
- utilise `Done`, `Undo Done`, `Discard` et `Undo Discard` pour gerer les combinaisons candidates
- consulte le panneau `current candidate` pour voir l'etat de la paire courante
- ouvre l'historique si tu veux recharger une suggestion precedente
- consulte les trois onglets : graphe, infos, statistiques
- dans l'onglet graphe, utilise la souris pour zoomer et deplacer la vue

## Onglets

- `Graphe` : rendu natif, recherche, recentrage, sous-graphe, filtre par poids, details du noeud selectionne
- `Infos` : tables des noeuds, edges et combinaisons `discarded`
- `Statistiques` : courbes par poids et liste des recettes candidates restantes par poids

## Limite actuelle

Sur une vraie sauvegarde Infinite Craft, il peut y avoir des dizaines de millions de paires possibles. L'application travaille donc sur une selection exploitable de combinaisons candidates pour l'interface. Cela reste une liste de paires non testees, pas une prediction des resultats.

Pour les tres gros graphes :

- les donnees completes restent chargees pour les tables et statistiques
- le rendu visuel peut etre reduit a un sous-graphe plus exploitable
- les positions de layout sont mises en cache localement

## Modele du graphe

- chaque element est un noeud
- les starters `Water`, `Fire`, `Wind`, `Earth` ont un poids de `0`
- tout autre noeud a pour poids minimal `poids(element_1) + poids(element_2) + 1`
- si plusieurs recettes produisent un meme element, le poids minimal est conserve
- une recette `A + B = C` cree jusqu'a deux edges : `A -> C` et `B -> C`
- si une edge existe deja, elle n'est pas recreee
- chaque edge stocke la liste des co-elements rencontres sur cette relation
- le poids d'une edge est `len(liste_des_co_elements)`
