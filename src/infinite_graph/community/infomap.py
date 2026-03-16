"""Direct Infomap runner and benchmark-based estimation helpers."""

from __future__ import annotations

from collections import defaultdict
import math

import infomap as infomap_package
import networkx as nx
from cdlib.classes import NodeClustering

from .estimation import build_graph_structure_features, build_reference_points, finalize_estimate


INFOMAP_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 2.65, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0041, 2.0),
        (20.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 0.0022, 3.0),
        (20.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 0.0013, 3.0),
        (100.0, 2.92, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0120, 2.0),
        (100.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 0.0101, 8.0),
        (100.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 0.0108, 9.0),
        (300.0, 2.9766666667, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0407, 2.0),
        (300.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 0.0380, 5.0),
        (300.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 0.0326, 6.0),
        (1000.0, 2.992, 0.0, 0.0, 1.0, 1.0, 0.0, 0.1784, 3.0),
        (1000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 0.1565, 3.0),
        (1000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 0.1852, 3.0),
        (3000.0, 2.9973333333, 0.0, 0.0, 1.0, 1.0, 0.0, 0.7432, 2.0),
        (3000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 0.5273, 6.0),
        (3000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 0.6057, 6.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 1.0, 0.0, 2.6611, 3.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 2.2888, 3.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 2.2310, 4.0),
        (30000.0, 2.9997333333, 0.0, 0.0, 1.0, 1.0, 0.0, 9.0143, 2.0),
        (30000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 7.2460, 6.0),
        (30000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 8.6127, 5.0),
        (100000.0, 2.99992, 0.0, 0.0, 1.0, 1.0, 0.0, 38.5306, 2.0),
        (100000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 0.0, 27.1643, 3.0),
        (100000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 0.0, 29.5149, 3.0),
        (10000.0, 2.9992, 0.0, 0.0, 5.0, 1.0, 0.0, 9.5182, 3.0),
        (10000.0, 2.9992, 0.0, 0.0, 10.0, 1.0, 0.0, 17.1222, 3.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 0.5, 0.0, 3.8457, 2.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 2.0, 0.0, 1.8004, 3.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 5.0, 0.0, 1.0701, 2.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 1.0, 2.0, 2.8844, 2.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 1.0, 3.0, 2.6029, 3.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 1.0, 5.0, 2.2981, 5.0),
        (10000.0, 2.9992, 0.0, 0.0, 1.0, 1.0, 10.0, 2.3998, 10.0),
        (10000.0, 3.0, 0.0, 1.5, 5.0, 1.0, 0.0, 7.5531, 3.0),
        (10000.0, 3.0, 0.0, 1.5, 10.0, 1.0, 0.0, 15.3499, 3.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 0.5, 0.0, 3.0370, 5.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 2.0, 0.0, 1.4859, 8.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 5.0, 0.0, 0.8582, 5.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 2.0, 2.9273, 2.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 3.0, 2.7801, 3.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 5.0, 2.7306, 5.0),
        (10000.0, 3.0, 0.0, 1.5, 1.0, 1.0, 10.0, 2.4516, 10.0),
        (10000.0, 4.0, 1.0, 1.5, 5.0, 1.0, 0.0, 8.9449, 4.0),
        (10000.0, 4.0, 1.0, 1.5, 10.0, 1.0, 0.0, 15.3975, 4.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 0.5, 0.0, 3.1494, 4.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 2.0, 0.0, 1.5132, 9.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 5.0, 0.0, 0.9269, 5.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 2.0, 2.5319, 2.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 3.0, 3.0355, 3.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 5.0, 2.2415, 5.0),
        (10000.0, 4.0, 1.0, 1.5, 1.0, 1.0, 10.0, 2.5937, 10.0),
    ),
    extra_keys=("num_trials", "markov_time", "preferred_modules"),
)


def infomap_reference_distance(
    features: dict[str, float],
    reference: dict[str, float],
) -> float:
    """Compute a weighted distance to an Infomap benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.8
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
        + abs(math.log((features["num_trials"] + 1.0) / (reference["num_trials"] + 1.0))) * 1.6
        + abs(math.log((features["markov_time"] + 0.01) / (reference["markov_time"] + 0.01)))
        * 1.2
        + abs(features["preferred_modules"] - reference["preferred_modules"]) * 0.35
    )


def run_direct_infomap(
    graph: nx.DiGraph | nx.Graph,
    flags: str = "",
    num_trials: int = 1,
    seed: int = 123,
    markov_time: float = 1.0,
    preferred_number_of_modules: int = 0,
) -> NodeClustering:
    """Run Infomap through the infomap package directly."""
    legacy_flags = flags.strip()
    normalized_graph = nx.convert_node_labels_to_integers(graph, label_attribute="name")
    name_map = nx.get_node_attributes(normalized_graph, "name")
    communities_by_module: defaultdict[int, list[str]] = defaultdict(list)

    infomap_runner = infomap_package.Infomap(
        silent=True,
        no_file_output=True,
        directed=graph.is_directed(),
        num_trials=int(num_trials),
        seed=int(seed),
        markov_time=float(markov_time),
        preferred_number_of_modules=(
            None if int(preferred_number_of_modules) <= 0 else int(preferred_number_of_modules)
        ),
    )
    infomap_runner.add_nodes({int(node_id): str(name) for node_id, name in name_map.items()})

    for source, target, data in normalized_graph.edges(data=True):
        weight = data.get("weight")
        if weight is None:
            infomap_runner.add_link(source, target)
        else:
            infomap_runner.add_link(source, target, float(weight))

    infomap_runner.run()

    for node_id, module_id in infomap_runner.modules:
        communities_by_module[int(module_id)].append(str(name_map[int(node_id)]))

    communities = [list(nodes) for nodes in communities_by_module.values()]
    return NodeClustering(
        communities,
        graph,
        "Infomap",
        method_parameters={
            **({"legacy_flags": legacy_flags} if legacy_flags else {}),
            "num_trials": int(num_trials),
            "seed": int(seed),
            "markov_time": float(markov_time),
            **(
                {"preferred_number_of_modules": int(preferred_number_of_modules)}
                if int(preferred_number_of_modules) > 0
                else {}
            ),
        },
    )


def estimate_infomap_runtime_and_communities(
    graph: nx.DiGraph,
    num_trials: int = 1,
    seed: int = 123,
    markov_time: float = 1.0,
    preferred_number_of_modules: int = 0,
) -> dict[str, object]:
    """Estimate Infomap runtime and community count from project benchmarks."""
    del seed
    features = build_graph_structure_features(graph) | {
        "num_trials": float(max(1, int(num_trials))),
        "markov_time": float(max(0.01, float(markov_time))),
        "preferred_modules": float(max(0, int(preferred_number_of_modules))),
    }
    return finalize_estimate(
        features,
        INFOMAP_ESTIMATION_REFERENCE_POINTS,
        infomap_reference_distance,
    )
