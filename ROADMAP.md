# Roadmap

This roadmap describes the current state of the `Infinite Graph` project, what has already been completed, and the next possible steps.

## 1. Project foundations

- [x] Git repository initialized
- [x] Project pushed to GitHub
- [x] Clean Python project structure with `main.py` as the entry point
- [x] Code split into `src/infinite_graph`
- [x] Dependencies centralized in `requirements.txt`
- [x] Base documentation in `README.md`
- [x] Add a license if needed
- [x] Clarify the product vision in the `README`
- [x] Add a changelog as the project grows

## 2. Save loading and validation

- [x] Support the real Infinite Craft save format with `items`
- [x] Support a simplified JSON test format
- [x] Normalize recipes as `left`, `right`, `result`
- [x] Validate required starter elements: `Water`, `Fire`, `Wind`, `Earth`
- [x] Show an explicit error if a starter is missing
- [x] Better handle partially corrupted saves
- [x] Report ignored invalid recipes
- [x] Add parsing unit tests

## 3. Graph model

- [x] Each element is a node
- [x] Each recipe `A + B = C` creates up to two edges: `A -> C` and `B -> C`
- [x] Merge already existing edges
- [x] Preserve the co-element list on each edge
- [x] Edge weight = `len(co_element_list)`
- [x] Compute minimal node weights
- [x] Starter nodes have weight `0`
- [x] Result weight = `weight(A) + weight(B) + 1`
- [x] Keep the minimal weight when multiple recipes produce the same result
- [x] Improve propagation with priority on lower weights
- [x] Add unit tests for weight computation
- [x] Add tests for edge merging
- [x] Add regression tests on mini saves

## 4. Graphical interface

- [x] Desktop Qt GUI
- [x] `Graph` tab
- [x] `Info` tab
- [x] `Statistics` tab
- [x] Native graph rendering with `pyqtgraph`
- [x] Current layout based on `spring layout`
- [x] Zoom and pan in the graph view
- [x] Node table with weights
- [x] Edge table with weights and co-elements
- [x] Chart for completed recipe count by result weight
- [x] Chart for element count by weight
- [x] List of possible missing recipe counts by weight
- [x] Node selection in the graph
- [x] Highlight neighboring nodes
- [x] Selected-node details panel
- [x] Search for an element in the graph view
- [x] Auto-center on an element
- [x] Subgraph filtering
- [x] Min / max weight filtering
- [x] Layout settings exposed in the interface

## 5. Generation user experience

- [x] Run generation outside the main thread
- [x] Keep the window responsive during processing
- [x] Indeterminate loading bar
- [x] Show the current stage
- [x] Detailed progress during `spring layout`
- [x] Approximate ETA during layout computation
- [x] Real percentage progress bar
- [x] Finer progress stages
- [x] Display total generation time
- [x] Local layout cache to avoid recomputing everything

## 6. Candidate combination workflow

- [x] Two fields: `Element 1` and `Element 2`
- [x] `Random` button
- [x] `Cheapest` button
- [x] `Done` button
- [x] `Discard` button
- [x] `Random` suggests an unfinished random combination
- [x] `Cheapest` suggests a combination with the lowest result weight
- [x] `Done` marks a combination as completed for the current session only
- [x] `Discard` marks a combination as impossible persistently
- [x] `Random` and `Cheapest` exclude known recipes
- [x] `Random` and `Cheapest` exclude discarded combinations
- [x] `Random` and `Cheapest` exclude session-done combinations
- [x] Fields are editable
- [x] Clicking a field copies its content to the clipboard
- [x] Fields are cleared after `Done`
- [x] Fields are cleared after `Discard`
- [x] No popup for `Done`
- [x] Element name auto-completion
- [x] `Undo Done` button
- [x] `Undo Discard` button
- [x] Button to jump directly to the next suggestion
- [x] Local history of the latest suggestions
- [x] Live validation of typed element names

## 7. Local persistence

- [x] Global `discarded.json` file
- [x] Discarded combinations are global and independent of the loaded save
- [x] Backward compatibility with the old `discarded.json` format
- [x] Rewrite to the new global format
- [x] Interface to browse discarded combinations
- [x] Manual removal of a discarded combination
- [x] Full reset of `discarded.json`
- [x] Manual import / export when needed

## 8. Cleanup already completed

- [x] CLI removed
- [x] HTML rendering removed
- [x] Unused web assets removed
- [x] CSV export removed
- [x] Documentation cleaned accordingly
- [x] Clean `.gitignore` if some ignored paths are no longer used
- [x] Check whether dead files remain in the repository

## 9. Software quality

- [x] Unit tests for save loading
- [x] Unit tests for starter validation
- [x] Unit tests for weight computation
- [x] Unit tests for edge merging
- [x] Unit tests for `Random`
- [x] Unit tests for `Cheapest`
- [x] Unit tests for `Done`
- [x] Unit tests for `Discard`
- [x] Persistence tests for `discarded.json`
- [x] Minimal GUI tests
- [x] Formatter added
- [x] Linter added
- [x] GitHub Actions CI added

## 10. Performance

- [x] Heavy processing moved out of the main thread
- [x] Current processing state visible to the user
- [x] Optimize the `spring layout`
- [x] Cache node positions
- [x] Avoid full recomputation when only the interface changes
- [x] Compute reduced subgraphs instead of the full graph when needed
- [x] Index candidate combinations more efficiently

## 11. Product UX

- [x] Explain why a combination is no longer suggested
- [x] Add a `current candidate` panel
- [x] Show the remaining candidate combination count

## 12. Future UX improvements

- [x] Unify all interface wording
- [x] Responsive layout for desktop / smaller windows
- [x] Persistent UI preferences
- [x] Search / filtering in `Info` tables
- [x] Context actions from the graph
- [x] Export the graph as an image
- [x] Real statistics view polish
- [x] Complete lexical cleanup of the interface
- [x] More UX-oriented error handling

## 13. Mono-community analysis

- [x] Add `cdlib` to the project dependencies
- [x] Add a `community_analysis.py` module
- [x] Build a CDlib graph from the current graph data
- [x] Keep the graph directed for community analysis
- [x] Use edge weights only
- [x] Explicitly ignore node weights
- [x] Add a `Communities` tab to the interface
- [x] Add a mono-community algorithm selector
- [x] Evaluate the relevant mono-community CDlib algorithms for the directed weighted graph
- [x] Keep less compatible algorithms available with graph adaptation and user warnings
- [x] Document compatibility notes for every mono-community algorithm
- [x] Evaluate all available CDlib crisp mono-community algorithms
- [x] Expose `AGDL` in the algorithm selector
- [x] Expose `Async Fluid` in the algorithm selector
- [x] Expose `Bayan` in the algorithm selector
- [x] Expose `Belief` in the algorithm selector
- [x] Expose `CPM` in the algorithm selector
- [x] Expose `DER` in the algorithm selector
- [x] Expose `Eigenvector` in the algorithm selector
- [x] Expose `EM` in the algorithm selector
- [x] Expose `GA` in the algorithm selector
- [x] Expose `GDMP2` in the algorithm selector
- [x] Expose `Girvan-Newman` in the algorithm selector
- [x] Expose `Greedy Modularity` in the algorithm selector
- [x] Expose `Head/Tail` in the algorithm selector
- [x] Expose `Infomap` in the algorithm selector
- [x] Expose `Kcut` in the algorithm selector
- [x] Expose `Label Propagation Cordasco-Gargano` in the algorithm selector
- [x] Expose `Leiden` in the algorithm selector
- [x] Expose `Louvain` in the algorithm selector
- [x] Expose `LSWL` in the algorithm selector
- [x] Expose `LSWL Plus` in the algorithm selector
- [x] Expose `Markov Clustering` in the algorithm selector
- [x] Expose `MCODE` in the algorithm selector
- [x] Expose `Mod M` in the algorithm selector
- [x] Expose `Mod R` in the algorithm selector
- [x] Expose `Paris` in the algorithm selector
- [x] Expose `PyCombo` in the algorithm selector
- [x] Expose `RBER Pots` in the algorithm selector
- [x] Expose `RB Pots` in the algorithm selector
- [x] Expose `Ricci Community` in the algorithm selector on Unix-like systems only
- [x] Expose `R Spectral Clustering` in the algorithm selector
- [x] Expose `SCAN` in the algorithm selector
- [x] Expose `Significance Communities` in the algorithm selector
- [x] Expose `Spinglass` in the algorithm selector
- [x] Expose `Surprise Communities` in the algorithm selector
- [x] Expose `Walktrap` in the algorithm selector
- [x] Expose `SBM DL` in the algorithm selector on Unix-like systems only
- [x] Expose `SBM DL Nested` in the algorithm selector on Unix-like systems only
- [x] Expose `Spectral` in the algorithm selector
- [x] Expose `Threshold Clustering` in the algorithm selector
- [x] Integrate `AGDL` execution from the `Communities` tab
- [ ] Integrate `Async Fluid` execution from the `Communities` tab
- [ ] Integrate `Bayan` execution from the `Communities` tab
- [ ] Integrate `Belief` execution from the `Communities` tab
- [ ] Integrate `CPM` execution from the `Communities` tab
- [ ] Integrate `DER` execution from the `Communities` tab
- [ ] Integrate `Eigenvector` execution from the `Communities` tab
- [ ] Integrate `EM` execution from the `Communities` tab
- [ ] Integrate `GA` execution from the `Communities` tab
- [ ] Integrate `GDMP2` execution from the `Communities` tab
- [ ] Integrate `Girvan-Newman` execution from the `Communities` tab
- [ ] Integrate `Greedy Modularity` execution from the `Communities` tab
- [ ] Integrate `Head/Tail` execution from the `Communities` tab
- [ ] Integrate `Infomap` execution from the `Communities` tab
- [ ] Integrate `Kcut` execution from the `Communities` tab
- [ ] Integrate `Label Propagation Cordasco-Gargano` execution from the `Communities` tab
- [ ] Integrate `Leiden` execution from the `Communities` tab
- [ ] Integrate `Louvain` execution from the `Communities` tab
- [ ] Integrate `LSWL` execution from the `Communities` tab
- [ ] Integrate `LSWL Plus` execution from the `Communities` tab
- [ ] Integrate `Markov Clustering` execution from the `Communities` tab
- [ ] Integrate `MCODE` execution from the `Communities` tab
- [ ] Integrate `Mod M` execution from the `Communities` tab
- [ ] Integrate `Mod R` execution from the `Communities` tab
- [ ] Integrate `Paris` execution from the `Communities` tab
- [ ] Integrate `PyCombo` execution from the `Communities` tab
- [ ] Integrate `RBER Pots` execution from the `Communities` tab
- [ ] Integrate `RB Pots` execution from the `Communities` tab
- [ ] Integrate `Ricci Community` execution from the `Communities` tab
- [ ] Integrate `R Spectral Clustering` execution from the `Communities` tab
- [ ] Integrate `SCAN` execution from the `Communities` tab
- [ ] Integrate `Significance Communities` execution from the `Communities` tab
- [ ] Integrate `Spinglass` execution from the `Communities` tab
- [ ] Integrate `Surprise Communities` execution from the `Communities` tab
- [ ] Integrate `Walktrap` execution from the `Communities` tab
- [ ] Integrate `SBM DL` execution from the `Communities` tab
- [ ] Integrate `SBM DL Nested` execution from the `Communities` tab
- [ ] Integrate `Spectral` execution from the `Communities` tab
- [ ] Integrate `Threshold Clustering` execution from the `Communities` tab
- [ ] Allow running community detection from the GUI
- [ ] Show progress or at least a running state during computation
- [ ] Add a `Communities` panel or full tab content area
- [ ] Show the total number of detected communities
- [ ] Show min / max / average community size
- [ ] List detected communities
- [ ] Allow selecting a community
- [ ] Show the node list of the selected community
- [ ] Color the graph by community
- [ ] Add an option to disable community coloring
- [ ] Add a hierarchical layout by communities
- [ ] Compute a global `spring layout` between communities
- [ ] Compute a local `spring layout` inside each community
- [ ] Combine both layouts to display node clusters by community
- [ ] Show the community identifier in the node table
- [ ] Add a summary of the parameters used for the computation
- [ ] Add the basic parameters of mono-community algorithms
- [x] Add a strong documented warning for unstable `AGDL` execution
- [ ] Expose at least the resolution parameter for `RB Pots`
- [ ] Gracefully handle errors when an algorithm backend is missing
- [ ] Add unit tests for building the CDlib graph
- [ ] Add unit tests for mono-community outputs
- [ ] Add minimal GUI tests for the community computation flow
- [ ] Visually compare the retained mono-community algorithms on a mini test save
