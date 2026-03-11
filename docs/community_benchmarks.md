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
