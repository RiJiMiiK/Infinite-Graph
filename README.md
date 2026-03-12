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
- dedicated tabs for:
  - `Graph`
  - `Info`
  - `Statistics`
  - `Communities`
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

### Communities tab

- mono-community analysis scaffold
- algorithm selector backed by CDlib metadata
- platform-aware algorithm visibility
- community summary, list, and details panels ready for the next analysis steps
- algorithm-specific parameter inputs for supported community methods such as `AGDL`
- pre-run warnings for high-risk algorithms before launching a community computation
- benchmark-based pre-run estimates for `Belief` runtime and expected community count
- benchmark-based pre-run estimates for `CPM` runtime and expected community count
- benchmark-based pre-run estimates for `Async Fluid` runtime and expected community count
- benchmark-based pre-run estimates for `DER` runtime and expected community count
- benchmark-based pre-run estimates for `Eigenvector` runtime and expected community count
- guided warning/error handling for `Eigenvector` ARPACK failures on large graphs

Current visibility rules:

- `label_propagation_raghavan` is hidden because it is not exposed by the installed `cdlib 0.4.0`
- `ricci_community`, `sbm_dl`, and `sbm_dl_nested` are only shown on Unix-like systems

Current stability note:

- `AGDL` is available, but it is marked as experimental
- the pre-run warning now also includes:
  - an estimated runtime
  - an estimated community count
  - a low-confidence note
- benchmark runs reproduced upstream CDlib crashes on several graph families
- the failure also reproduces on the documented `karate_club_graph()` example in this environment
- treat `AGDL` as a best-effort option, not as a stable default
- detailed benchmark notes are tracked in `docs/community_benchmarks.md`

Current solver warning:

- `Bayan` is available, but it depends on Gurobi
- when a restricted Gurobi license is detected, the application shows a pre-run warning
- the main risk in this project comes from running it without a suitable full Gurobi license
- with only a restricted license, Bayan can hit the Gurobi size limit on relatively small graphs
- that failure may happen only after the solver has already spent an unknown amount of time running
- a real Infinite Graph save reproduced this with a run started around `01:00` that was still blocked when checked again around `07:00`
- that observation was made with a restricted Gurobi license only
- no equivalent runtime validation was completed with a full Gurobi license
- with a proper full license, this specific risk is expected to be much lower

Current `Belief` warning:

- `Belief` stays available, but the application shows a pre-run warning before execution
- the warning includes:
  - an estimated runtime for the current graph and parameter set
  - an estimated community count for the current graph and parameter set
- these estimates are calculated from project benchmark reference data rather than from hardcoded if/else thresholds
- they should be treated as heuristics, not guarantees
- benchmark notes also document a theory-based interpretation of why `Belief` can collapse to a single dominant community and why its runtime can increase sharply on some graph families

Current `CPM` warning:

- `CPM` stays available, and the application shows a pre-run warning before execution
- the warning includes:
  - an estimated runtime for the current graph and `resolution_parameter`
  - an estimated community count for the current graph and `resolution_parameter`
- these estimates are derived from project-side benchmarks on real Infinite Graph subgraphs and the full example save
- they should be treated as heuristics, not guarantees
- the main practical effect of `resolution_parameter` is fragmentation:
  - very low values can merge large portions of the graph
  - higher values can split the graph into many small communities very quickly

Current `Async Fluid` warning:

- `Async Fluid` stays available, and the application shows a lightweight pre-run warning before execution
- the warning includes:
  - an estimated runtime for the current graph and `k`
  - an estimated community count for the current graph and `k`
- the expected community count follows `k` by design for this method
- project benchmarks show that `Async Fluid` remains fast on the tested graph families, including at `1000` nodes

Current `DER` warning:

- `DER` stays available, and the application shows a lightweight pre-run warning before execution
- the warning includes:
  - an estimated runtime for the current graph and parameter set
  - an estimated community count for the current graph and parameter set
- benchmark runs showed that `DER` stays fast on the tested graph families, including very large synthetic cases
- the main runtime cost drivers observed were very large `walk_len` and `iter_bound` values
- the estimate is heuristic and should be treated as guidance only

Current `Eigenvector` warning:

- `Eigenvector` stays available, but the application warns on large graphs before execution
- the warning includes:
  - an estimated runtime
  - an estimated community count
  - an estimated ARPACK failure risk
- large saves can fail inside ARPACK with a numerical precision error instead of returning a partition
- if that happens, the GUI now shows a guided error message recommending a smaller subgraph or another algorithm

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
- `tools/test_crisp_algorithms.py`: manual crisp mono-community benchmark script
- `docs/community_benchmarks.md`: benchmark notes used to document community-algorithm behavior
- `docker/`: Linux benchmark containers for community algorithms
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

## Community benchmarking

Manual benchmark:

```bash
python tools/test_crisp_algorithms.py
```

Linux Docker benchmark:

```bash
docker build -f docker/community-linux.Dockerfile -t infinite-graph-community .
docker run --rm infinite-graph-community python3 tools/test_crisp_algorithms.py
```

Linux Python 3.13 benchmark:

```bash
docker build -f docker/community-linux-py313.Dockerfile -t infinite-graph-community-py313 .
docker run --rm infinite-graph-community-py313 python tools/test_crisp_algorithms.py
```

Validated benchmark summary:

- Windows + Python 3.12: `36 OK`, `4 errors`
- Windows + Python 3.13: `36 OK`, `4 errors`
- Linux + Python 3.12: `39 OK`, `1 error`
- Linux + Python 3.13: `37 OK`, `3 errors`

The only algorithm currently failing everywhere is `label_propagation_raghavan`, because the installed `cdlib 0.4.0` package does not expose that callable.

Additional benchmark note:

- `AGDL` is not hidden, but it is intentionally treated as unstable
- repeated matrix tests across graph size, orientation, weighting, cyclicity, self-loops, and parameter ranges up to `100`
  reproduced non-deterministic failure families in the upstream CDlib implementation
- `Bayan` is additionally constrained by the local Gurobi license, so runtime behavior can be dominated by the solver rather than by the graph algorithm itself

## Roadmap direction

The next major feature area is completing mono-community analysis on the directed weighted graph through CDlib and wiring the computation flow into the existing `Communities` tab.

Planned direction:

- dedicated `Communities` tab
- support for multiple mono-community algorithms
- graph coloring by community
- hierarchical community-aware graph layout

See [ROADMAP.md](ROADMAP.md) for the current plan.
