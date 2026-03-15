# Changelog

## Unreleased

- full native Qt GUI with `Graphe`, `Infos` and `Statistiques` tabs
- added a `Communities` tab scaffold for mono-community analysis
- support for real Infinite Craft saves based on `items`
- graph model with node weights and merged directed edges
- candidate workflow with `Random`, `Cheapest`, `Next`, `Done`, `Undo Done`, `Discard` and `Undo Discard`
- current candidate panel, local suggestion history and remaining candidate counter
- global `discarded.json` persistence with browse, remove, reset, import and export actions
- threaded generation with visible progress, total duration and cached spring layout
- graph interactions: node selection, neighbor highlight, selected-node details, search, centering, subgraph and weight filters
- UI cleanup and dark mode across the application and graph view
- added `community_analysis.py` for CDlib-backed mono-community metadata, graph preparation, and result summaries
- added a strong AGDL runtime warning in the community-analysis flow and documented its upstream instability
- added a benchmark-based `AGDL` preview estimate with runtime and estimated community count
- added a benchmark-based `Belief` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `CPM` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `Async Fluid` pre-run warning with estimated runtime and expected community count
- added a benchmark-based `DER` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `EM` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `GA` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `GDMP2` pre-run warning with estimated runtime and estimated community count
- added a benchmark-based `Eigenvector` pre-run estimate with runtime and estimated community count
- added guided warnings and error handling for `Eigenvector` ARPACK failures on large graphs
- added `tools/test_crisp_algorithms.py` and Docker benchmark environments for cross-platform crisp mono-community validation
- validated community algorithm availability across Windows/Linux and now hide:
  - `label_propagation_raghavan` everywhere
  - `ricci_community`, `sbm_dl`, and `sbm_dl_nested` on non-Unix systems
- test suite at `100%` coverage and `pylint` score at `10.00/10`

## 0.1.0 - 2026-03-08

- initial public project setup
