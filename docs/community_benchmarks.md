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
