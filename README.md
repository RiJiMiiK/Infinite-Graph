# Infinite Graph

Infinite Graph is a Python desktop application for exploring an Infinite Craft save file as a graph, inspecting its structure, and managing still-untested candidate combinations.

It is built as an interactive analysis tool, not as a static export utility.

## What the project does

Infinite Graph focuses on three things:

- graph exploration of discovered Infinite Craft elements
- candidate combination management for still-untested pairs
- structural analysis through node weights, edge aggregation, and statistics

The application loads a save, computes a directed weighted graph, and gives you tools to:

- inspect nodes and edges
- understand element depth through minimal node weights
- browse remaining candidate combinations
- mark combinations as done or discarded
- keep local working state while exploring a save

## Current feature set

### Save support

- real Infinite Craft save format based on `items`
- simplified JSON test format for fixtures and regression coverage
- graceful handling of partially corrupted saves
- warnings for ignored invalid entries or recipes
- validation of required starter elements:
  - `Water`
  - `Fire`
  - `Wind`
  - `Earth`

### Graph model

- each element is a node
- each recipe `A + B = C` creates up to two directed edges:
  - `A -> C`
  - `B -> C`
- edges are merged instead of duplicated
- each edge stores the list of co-elements seen on that relation
- edge weight equals the number of stored co-elements
- starter elements have node weight `0`
- all other node weights are computed as:
  - `weight(A) + weight(B) + 1`
- when multiple recipes produce the same element, the minimal weight is kept

### GUI

- full Qt desktop interface
- global dark mode
- responsive layout for large and smaller windows
- persistent UI preferences:
  - window size
  - panel visibility
  - splitter sizes
  - layout settings

### Graph tab

- native graph rendering with `pyqtgraph`
- zoom and pan
- spring layout with local cache
- search for an element
- automatic centering on selected elements
- node selection
- neighbor highlighting
- selected-node details panel
- subgraph filtering
- weight filtering
- graph image export
- graph context menu actions:
  - copy element name
  - use as `Element 1`
  - use as `Element 2`
  - search this element
  - set as subgraph center

### Candidate workflow

- `Random`
- `Cheapest`
- `Next`
- `Done`
- `Undo Done`
- `Discard`
- `Undo Discard`

The application also includes:

- editable element fields
- auto-completion for element names
- live validation of typed names
- `current candidate` panel
- local suggestion history
- remaining candidate count
- explanation of why a pair is no longer suggestible

### Discarded combination management

- global `discarded.json`
- independent from the loaded save
- browse discarded pairs in the `Info` tab
- manually remove a discarded pair
- reset the whole discarded list
- import and export discarded combinations

### Info tab

- node table
- edge table
- discarded combinations table
- search / filtering for the tables

### Statistics tab

- chart of completed recipe counts by result weight
- chart of element counts by weight
- missing recipe counts by result weight
- overview cards for the main statistics
- dark-mode styling consistent with the rest of the app

### Generation flow

- runs outside the main UI thread
- window remains responsive
- visible progress bar
- detailed stage messages
- percentage progress
- spring layout progress details
- total generation time shown

## Supported save formats

### Real Infinite Craft save

The main supported format is the real Infinite Craft save based on an `items` list.

Each item is interpreted as an element, and its `recipes` field is interpreted as the list of recipes that produce that element.

Example:

```json
{
  "id": 4,
  "text": "Steam",
  "recipes": [[0, 1]]
}
```

This is interpreted as:

- `Water + Fire -> Steam`

### Simplified test format

```json
{
  "elements": ["Water", "Fire", "Steam"],
  "recipes": [
    { "left": "Water", "right": "Fire", "result": "Steam" }
  ]
}
```

Accepted recipe key variants:

- `left` / `right` / `result`
- `first` / `second` / `result`
- `a` / `b` / `result`

Accepted element entry variants:

- plain string
- object with `name`
- object with `text`
- object with `result`

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the application

```bash
python main.py
```

## Typical workflow

1. Load an Infinite Craft save.
2. Click `Generate`.
3. Explore the graph, node table, edge table, and statistics.
4. Use `Random` or `Cheapest` to get a candidate combination.
5. Mark the pair as:
   - `Done` if you tested it in your current session
   - `Discard` if you want to permanently ignore it
6. Use `Undo Done` or `Undo Discard` when needed.
7. Use `Next` to defer a suggestion and move on.
8. Use history to revisit an earlier suggestion.

## Project structure

- `main.py`: application entry point
- `src/infinite_graph`: application code
- `tests`: full automated test suite
- `ROADMAP.md`: project roadmap
- `CHANGELOG.md`: release history
- `discarded.json`: global discarded combination storage
- `LICENSE`: project license

## Code quality

The project explicitly follows:

- `PEP 8`
- `PEP 257`
- `PEP 20`

Tools currently used:

- `black`
- `isort`
- `pylint`
- `pytest`
- `pytest-cov`

Current quality targets already reached:

- `100.00%` test coverage
- `pylint` score of `10.00/10`

Current CI:

- GitHub Actions runs `python -m pytest --cov --cov-report=term-missing`
- GitHub Actions runs `python -m pylint main.py src`

Internal module-size policy:

- warning from `800` lines
- failure from `1000` lines

## Performance notes

Large Infinite Craft saves can contain a huge number of possible pairs.

To keep the application usable:

- full data remains available for tables and statistics
- graph rendering may use a reduced subgraph when the graph is too large to display comfortably
- graph layout positions are cached locally
- candidate combinations are indexed for faster suggestion lookup

The candidate list shown by the application is a usable working set of still-untested pairs, not a prediction engine for actual recipe results.

## Roadmap direction

The next major feature area is mono-community analysis on the directed weighted graph through CDlib.

Planned direction:

- dedicated `Communities` tab
- support for multiple mono-community algorithms
- graph coloring by community
- hierarchical community-aware graph layout

See [ROADMAP.md](/c:/Users/youen/OneDrive/Bureau/Infinite_Graph/ROADMAP.md) for the current plan.
