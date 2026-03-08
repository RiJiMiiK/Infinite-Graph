# Infinite Graph

Petit projet Python pour visualiser une sauvegarde d'Infinite Craft sous forme de graphe et lister les combinaisons qui n'ont pas encore ete faites.

## Vision

Infinite Graph a pour but de servir d'outil d'exploration pour une sauvegarde Infinite Craft.

L'idee n'est pas seulement d'afficher un graphe, mais de :

- comprendre la structure des elements deja decouverts
- estimer leur profondeur via un poids minimal
- identifier rapidement des combinaisons encore non tentees
- suivre localement les combinaisons deja essayees ou jugees inutiles

Le projet est pense comme un outil desktop interactif, centre sur l'analyse et la prise de decision, plutot qu'un simple export statique.

## Fonctionnalites

- lecture d'une sauvegarde JSON
- support du vrai format de sauvegarde Infinite Craft (`items`)
- interface graphique Qt
- affichage natif du graphe dans l'application avec `pyqtgraph`
- format simple alternatif toujours supporte
- validation obligatoire des starters `Water`, `Fire`, `Wind`, `Earth`
- calcul d'un poids minimal pour chaque noeud
- fusion des recettes en edges uniques avec liste des co-elements
- prise en compte d'un fichier global `discarded.json` pour exclure des combinaisons impossibles, quelle que soit la save chargee

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
- optionnellement renseigne un `Element cible` pour ne chercher que les paires manquantes de cet element
- utilise `Random`, `Cheapest`, `Done` et `Discard` pour gerer les combinaisons candidates
- clique sur `Generer`
- consulte les trois onglets : graphe, infos, statistiques
- dans l'onglet graphe, utilise la souris pour zoomer et deplacer la vue

## Limite actuelle

Sur une vraie sauvegarde Infinite Craft, il peut y avoir des dizaines de millions de paires possibles. L'application travaille donc sur une selection exploitable de combinaisons candidates pour l'interface. Cela reste une liste de paires non testees, pas une prediction des resultats.

## Modele du graphe

- chaque element est un noeud
- les starters `Water`, `Fire`, `Wind`, `Earth` ont un poids de `0`
- tout autre noeud a pour poids minimal `poids(element_1) + poids(element_2) + 1`
- si plusieurs recettes produisent un meme element, le poids minimal est conserve
- une recette `A + B = C` cree jusqu'a deux edges : `A -> C` et `B -> C`
- si une edge existe deja, elle n'est pas recreee
- chaque edge stocke la liste des co-elements rencontres sur cette relation
- le poids d'une edge est `len(liste_des_co_elements)`
