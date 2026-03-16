# Community Benchmarks

This file records the project-side benchmark observations used to document risky or expensive community algorithms.

## AGDL

`AGDL` is currently treated as experimental.

Observed issues:

- repeatable crashes on multiple weighted graph families
- failures reproduced on the documented `karate_club_graph()` example in this environment
- behavior appears to depend more on graph structure than on the `kc` / `number_communities` parameters

Project consequence:

- `AGDL` stays available, but it is documented as unstable
- the GUI shows a strong warning before/after use
- the pre-run popup now also includes:
  - a benchmark-based runtime estimate
  - a benchmark-based estimated community count
  - an explicit low-confidence note because only a subset of AGDL benchmark cases completed reliably

## Belief

`Belief` is not blocked, but it can become expensive quickly.

### Theory note

The project benchmark behavior is consistent with the paper behind the method:

- `Belief` is not simply looking for one "best" partition
- it tries to recover a consensus among many high-modularity partitions
- if the graph does not present a strong enough consensus signal, the method can collapse back to a very coarse solution
- in practice, this can mean a single dominant community even when smaller graphs or different parameters previously produced more groups

This also helps explain the runtime behavior:

- the paper discusses different phases such as `retrieval`, `paramagnetic`, and `spin glass`
- near difficult transition regions, convergence can become much slower
- this matches the project benchmarks, where some graph families and parameter sets become much more expensive without producing richer partitions

Project interpretation:

- getting `1` community is not automatically a bug
- it can mean that the method does not see a statistically robust community structure under the current graph adaptation and parameters
- this is especially relevant here because `Belief` is currently run on an undirected unweighted view of the Infinite Graph community graph
- dropping direction and weights may weaken the structural signal before the algorithm even starts

### Runtime baselines with default GUI parameters

Graph family notes:

- `acyclic`: directed weighted acyclic clustered graph
- `cyclic`: directed weighted clustered graph with reciprocal cross-links
- `cyclic_self`: same as `cyclic` plus one self-loop per node

Default parameters:

- `max_it=100`
- `eps=0.0001`
- `reruns_if_not_conv=5`
- `threshold=0.005`
- `q_max=7`

Measured runtimes:

| Nodes | Acyclic | Cyclic | Cyclic + self-loops |
| --- | ---: | ---: | ---: |
| 20 | 8.36s | 5.04s | 4.87s |
| 100 | 14.87s | 14.95s | 8.93s |
| 300 | 39.49s | 41.93s | 24.94s |
| 1000 | 6m 02.78s | 9m 16.23s | 4m 43.90s |

### Parameter exploration on 20-node graphs

Grid:

- `max_it`: `25`, `100`
- `eps`: `0.0001`, `0.001`
- `reruns_if_not_conv`: `1`, `5`
- `threshold`: `0.001`, `0.01`
- `q_max`: `3`, `7`, `12`

Observed outcome:

- `acyclic`: always `1` community
- `cyclic`: `1` or `2` communities depending on parameters
- `cyclic_self`: `1` or `2` communities depending on parameters

### Parameter follow-up on larger cyclic graphs with self-loops

Interesting observations:

- parameter sets that split `20` nodes do not necessarily generalize to `50`, `100`, `300`, or `1000`
- on `50` and `100` nodes, some settings still yield `2` communities
- on `300` nodes, one tested setting yielded `2` communities and another yielded `5`
- on `1000` nodes, the previously promising settings collapsed back to `1` community

Project consequence:

- the GUI shows a pre-run `Belief` popup
- the popup includes a benchmark-based runtime estimate
- the popup also includes a benchmark-based estimated community count
- both estimates are heuristic and should be treated as guidance only

## Bayan

`Bayan` depends on Gurobi.

Observed risk:

- with a restricted Gurobi license, runs can spend an effectively indefinite amount of time inside the solver before failing on license limits
- on a real Infinite Graph save, a run started around `01:00` and was still running when checked again around `07:00`

Project consequence:

- the GUI shows a strong pre-run warning before launching `Bayan`
- the warning is especially explicit when a restricted Gurobi license is detected

## CPM

`CPM` is fast enough for interactive use in this project, but it is highly sensitive to `resolution_parameter`.

### Real-graph benchmark basis

The project benchmark was rerun on:

- BFS subgraphs extracted from a real Infinite Graph save
- the full example save graph

Observed pattern:

- very low `resolution_parameter` values can collapse a graph to a single community
- larger values quickly increase fragmentation
- on the full example graph, `resolution_parameter=1.0` produced a very fragmented result, not a runtime problem

Representative results:

| Graph | Resolution | Communities | Runtime |
| --- | ---: | ---: | ---: |
| BFS 100 | `0.001` | `1` | `~0.006s` |
| BFS 100 | `1.0` | `73` | `~0.018s` |
| BFS 300 | `0.01` | `49` | `~0.035s` |
| BFS 300 | `1.0` | `196` | `~0.042s` |
| BFS 1000 | `0.01` | `263` | `~5.3s` |
| BFS 1000 | `1.0` | `546` | `~0.324s` |
| Full graph (`10195` nodes) | `0.001` | `1545` | `~7.4s` |
| Full graph (`10195` nodes) | `1.0` | `7630` | `~12.1s` |

Project consequence:

- the GUI shows a pre-run `CPM` popup
- the popup includes a benchmark-based runtime estimate
- the popup also includes a benchmark-based estimated community count
- both estimates are heuristic and should be treated as guidance only

## Async Fluid

`Async Fluid` is fast on the graph families tested for this project.

### Runtime baselines

Benchmarks were run on undirected graph families with:

- `acyclic`
- `cyclic`
- `cyclic_self`

and with `k` in `{2, 3, 5}`.

Observed runtimes:

| Nodes | Acyclic | Cyclic | Cyclic + self-loops |
| --- | ---: | ---: | ---: |
| 20 | `0.0003s` to `0.0008s` | `0.0002s` to `0.0006s` | `0.0003s` to `0.0004s` |
| 100 | `0.0059s` to `0.0133s` | `0.0024s` to `0.0027s` | `0.0026s` to `0.0040s` |
| 300 | `0.0351s` to `0.0648s` | `0.0145s` to `0.0296s` | `0.0163s` to `0.0199s` |
| 1000 | `0.2049s` to `0.4329s` | `0.1797s` to `0.5014s` | `0.2746s` to `0.3410s` |

Observed behavior:

- runtime stays low even at `1000` nodes
- the returned community count follows `k`, which is expected for this method

Project consequence:

- the GUI shows a lightweight pre-run `Async Fluid` popup
- the popup includes a benchmark-based runtime estimate
- it also reminds the user that the expected number of communities follows `k`

## DER

`DER` stayed fast across the project benchmark families, including larger graphs.

### Runtime baselines

Initial benchmark families:

- `acyclic`
- `cyclic`
- `cyclic_self`

with default-style parameters on weighted undirected graph views.

Observed runtimes:

| Nodes | Acyclic | Cyclic | Cyclic + self-loops |
| --- | ---: | ---: | ---: |
| 20 | `0.0028s` to `0.0038s` | `0.0021s` to `0.0034s` | `0.0021s` to `0.0036s` |
| 100 | `0.0028s` to `0.0085s` | `0.0033s` to `0.0064s` | `0.0028s` to `0.0060s` |
| 300 | `0.0044s` to `0.0088s` | `0.0051s` to `0.0075s` | `0.0055s` to `0.0088s` |
| 1000 | `0.0112s` to `0.0178s` | `0.0114s` to `0.0153s` | `0.0124s` to `0.0178s` |
| 3000 | `0.0287s` to `0.0962s` | `0.0289s` to `0.0363s` | `0.0331s` to `0.0425s` |
| 10000 | `0.0911s` to `0.2122s` | `0.0899s` to `0.2654s` | `0.1047s` to `0.2122s` |

### Extended parameter exploration

Broader tests pushed the parameter ranges further:

- `walk_len` up to `100`
- `threshold` from `1e-09` to `0.5`
- `iter_bound` up to `1000`

On a reduced extreme grid at `10000` nodes:

- `acyclic`: `0.1021s` to `4.3012s`
- `cyclic`: `0.1202s` to `4.7252s`
- `cyclic_self`: `0.1400s` to `6.0624s`

Observed behavior:

- the returned community count stayed at `2` on the tested synthetic families
- the main runtime cost drivers were very large `walk_len` and `iter_bound` values
- even then, DER remained practical compared with the slower algorithms benchmarked in this project

Project consequence:

- the GUI shows a lightweight pre-run `DER` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- the message explicitly notes that extreme `walk_len` and `iter_bound` values can slow large runs

## EM

`EM` stayed practical across the benchmark families tested in this project.

### Runtime baselines with varying `k`

Observed pattern:

- the detected community count follows `k`
- runtime grows with `k`
- the slowest observed family was `acyclic`

Representative points:

- `1000` nodes
  - `acyclic`, `k=2` -> `0.0429s`
  - `acyclic`, `k=10` -> `0.2529s`
  - `cyclic`, `k=10` -> `0.0353s`
  - `cyclic_self`, `k=10` -> `0.0318s`
- `10000` nodes
  - `acyclic`, `k=10` -> `11.6020s`
  - `acyclic`, `k=30` -> `22.2000s`
  - `cyclic`, `k=30` -> `1.0561s`
  - `cyclic_self`, `k=30` -> `1.0221s`

### Product consequence

- the GUI shows a lightweight pre-run `EM` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- it explicitly reflects that large acyclic-like graphs with high `k` are the costliest observed cases

## Eigenvector

`Eigenvector` stayed fast on small and medium synthetic graph families, but became slower and less numerically stable on larger ones.

### Runtime and community-count baselines

- `20` nodes:
  - `acyclic`: `0.0014s`, `4` communities
  - `cyclic`: `0.0006s`, `4` communities
  - `cyclic_self`: `0.0009s`, `4` communities
- `100` nodes:
  - `acyclic`: `0.0027s`, `8` communities
  - `cyclic`: `0.0023s`, `8` communities
  - `cyclic_self`: `0.0026s`, `8` communities
- `300` nodes:
  - `acyclic`: `0.0151s`, `20` communities
  - `cyclic`: `0.0161s`, `16` communities
  - `cyclic_self`: `0.0154s`, `16` communities
- `1000` nodes:
  - `acyclic`: `0.1397s`, `33` communities
  - `cyclic`: `0.1572s`, `32` communities
  - `cyclic_self`: `0.1645s`, `32` communities
- `3000` nodes:
  - `acyclic`: `3.9089s`, `54` communities
  - `cyclic`: `5.7967s`, `32` communities
  - `cyclic_self`: `4.8009s`, `64` communities

Project example save:
- runtime before failure: `6.5531s`
- result: `ARPACK` precision failure

### Product consequence

- the GUI shows a pre-run `Eigenvector` popup on large graphs
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- it also surfaces an estimated `ARPACK` failure risk level

## GA

`GA` is available, but it becomes expensive quickly as graph size grows.

### Runtime baselines

Default-style benchmark settings:

- `population=300`
- `generation=30`
- `r=1.5`

Observed runtimes:

| Nodes | Acyclic | Cyclic | Cyclic + self-loops |
| --- | ---: | ---: | ---: |
| 20 | `8.22s` | `8.58s` | `8.18s` |
| 50 | `13.19s` | `12.79s` | `12.07s` |
| 100 | `23.03s` | `24.51s` | `24.10s` |
| 150 | `55.44s` | `54.09s` | `47.00s` |
| 200 | `90.98s` | `88.87s` | `74.91s` |
| 250 | `149.19s` | `146.96s` | `123.52s` |
| 300 | `209.75s` | `208.49s` | `176.76s` |
| 350 | `288.95s` | `283.01s` | `239.78s` |
| 400 | `382.96s` | `382.88s` | `309.22s` |
| 450 | `673.48s` | `665.82s` | `552.33s` |
| 500 | `816.01s` | `812.86s` | `691.79s` |

### Parameter exploration on 100-node graphs

Main observations:

- `population` is the main runtime driver
- `generation` is the secondary runtime driver
- `r` mostly changes fragmentation rather than cost

Representative points:

- `population=50`, `generation=30`, `r=1.5`
  - `acyclic`: `4.77s`
  - `cyclic`: `3.31s`
  - `cyclic_self`: `3.24s`
- `population=600`, `generation=30`, `r=1.5`
  - `acyclic`: `50.28s`
  - `cyclic`: `58.88s`
  - `cyclic_self`: `57.24s`
- `population=300`, `generation=60`, `r=1.5`
  - `acyclic`: `35.72s`
  - `cyclic`: `32.09s`
  - `cyclic_self`: `27.43s`

Fragmentation effect of `r` on 100-node graphs:

- `acyclic`
  - `r=0.5` -> `16` communities
  - `r=2.0` -> `23` communities
- `cyclic`
  - `r=0.5` -> `15` communities
  - `r=2.0` -> `22` communities
- `cyclic_self`
  - `r=0.5` -> `22` communities
  - `r=3.0` -> `42` communities

Project consequence:

- the GUI shows a pre-run `GA` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- the warning explicitly notes that `population` dominates runtime, `generation` is the second cost driver, and `r` mostly changes fragmentation

## GDMP2

`GDMP2` stayed fast on smaller benchmark graphs, but it showed a structural recursion limit on larger ones in this project environment.

### Runtime and threshold exploration

Default-style benchmark results:

- `20` nodes
  - `acyclic`: `0.0054s`, `1` community
  - `cyclic`: `0.0037s`, `1` community
  - `cyclic_self`: `0.0043s`, `1` community
- `100` nodes
  - `acyclic`: `0.0769s`, `1` community
  - `cyclic`: `0.0709s`, `1` community
  - `cyclic_self`: `0.0755s`, `1` community
- `300` nodes
  - `acyclic`: `0.8507s`, `1` community
  - `cyclic`: `0.7307s`, `1` community
  - `cyclic_self`: `0.6642s`, `1` community

At `1000` nodes, every tested family failed with `RecursionError`, with runtimes around `14s` to `19s` before the crash.

Threshold exploration showed:

- on `300` nodes, `min_threshold` changes fragmentation
- very small thresholds such as `0.001` and `0.01` can collapse the synthetic graphs into a single giant community
- intermediate thresholds such as `0.05` can split some `acyclic` cases into `2` communities
- higher thresholds shrink the dominant community but still often leave the synthetic result at `1` community
- on `1000` nodes, none of the tested `min_threshold` values avoided the recursion failure

Project consequence:

- the GUI now shows a pre-run `GDMP2` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- it explicitly surfaces an estimated recursion-failure risk
- the warning states that changing `min_threshold` can alter fragmentation, but did not remove the large-graph recursion problem in project benchmarks

## Girvan-Newman

`Girvan-Newman` is available, but runtime rises quickly with both graph size and `level`.

### Runtime and `level` exploration

Benchmark graph families:

- `acyclic`
- `cyclic`
- `cyclic_self`

Representative results with `level=3`:

- `20` nodes
  - `acyclic`: `0.0201s`, `4` communities
  - `cyclic`: `0.0325s`, `4` communities
  - `cyclic_self`: `0.0344s`, `4` communities
- `100` nodes
  - `acyclic`: `0.3187s`, `4` communities
  - `cyclic`: `0.7276s`, `4` communities
  - `cyclic_self`: `0.7078s`, `4` communities
- `300` nodes
  - `acyclic`: `3.0414s`, `4` communities
  - `cyclic`: `6.9848s`, `4` communities
  - `cyclic_self`: `6.7630s`, `4` communities
- `1000` nodes
  - `acyclic`: `9.4773s`, `4` communities
  - `cyclic`: `17.9428s`, `4` communities
  - `cyclic_self`: `18.8398s`, `4` communities

A dedicated `10000`-node run did not finish within more than one hour in this environment.

### `level` follow-up

Observed pattern on `300` and `1000` nodes:

- runtime grows as `level` grows
- on the tested graph families, the returned community count tracked `level + 1` for `level >= 1`

Representative points:

- `300 | acyclic`
  - `level=1` -> `0.4279s`, `2` communities
  - `level=3` -> `0.7638s`, `4`
  - `level=10` -> `1.3286s`, `11`
- `1000 | cyclic`
  - `level=1` -> `7.5776s`, `2`
  - `level=3` -> `18.5216s`, `4`
  - `level=10` -> `20.1967s`, `11`

Special note:

- although the documentation mentions `level=-1` for highest modularity, the installed environment returned an empty partition for that mode during project benchmarks

Project consequence:

- the GUI now shows a pre-run `Girvan-Newman` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- it explicitly notes the observed cost growth with size and `level`
- it also warns that `level=-1` behaved unexpectedly in the project environment

## Greedy Modularity

`Greedy Modularity` stayed fast across the project benchmark families, including at `10000` nodes.

### Runtime baselines

Benchmarks were run on weighted undirected graph views for:

- `acyclic`
- `cyclic`
- `cyclic_self`

Observed results:

| Nodes | Acyclic | Cyclic | Cyclic + self-loops |
| --- | ---: | ---: | ---: |
| 20 | `0.0037s`, `5` communities | `0.0029s`, `4` | `0.0027s`, `6` |
| 100 | `0.0087s`, `17` | `0.0102s`, `16` | `0.0096s`, `17` |
| 300 | `0.0494s`, `25` | `0.0561s`, `25` | `0.0535s`, `25` |
| 1000 | `0.1777s`, `41` | `0.1601s`, `41` | `0.1901s`, `45` |
| 3000 | `0.5798s`, `64` | `0.6175s`, `65` | `0.5745s`, `65` |
| 10000 | `2.0790s`, `105` | `2.1120s`, `105` | `2.1691s`, `208` |

Project consequence:

- the GUI now shows a lightweight pre-run `Greedy Modularity` popup
- the popup includes a benchmark-based runtime estimate
- it also includes a benchmark-based estimated community count
- the message explicitly notes that this method stayed fast in the project benchmarks
