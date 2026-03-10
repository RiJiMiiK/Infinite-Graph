"""Manual runner for CDlib crisp mono-community algorithms."""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Any

import networkx as nx

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infinite_graph.community_analysis import (
    get_mono_community_algorithm_evaluation,
    run_mono_community_algorithm,
    summarize_mono_community_result,
)


def build_demo_graph() -> nx.DiGraph:
    """Build a small directed weighted graph with about 20 nodes."""
    graph = nx.DiGraph()

    communities = {
        "alchemy": ["Water", "Fire", "Steam", "Smoke", "Cloud", "Rain"],
        "nature": ["Earth", "Mud", "Plant", "Tree", "Forest", "Seed", "Flower"],
        "life": ["Wind", "Dust", "Energy", "Life", "Human", "Animal", "Bird"],
    }

    for nodes in communities.values():
        for node in nodes:
            graph.add_node(node)

    weighted_edges = [
        ("Water", "Steam", 3),
        ("Fire", "Steam", 3),
        ("Steam", "Cloud", 2),
        ("Smoke", "Cloud", 1),
        ("Cloud", "Rain", 2),
        ("Earth", "Mud", 3),
        ("Water", "Mud", 3),
        ("Mud", "Plant", 2),
        ("Plant", "Tree", 2),
        ("Tree", "Forest", 2),
        ("Plant", "Flower", 1),
        ("Tree", "Seed", 1),
        ("Wind", "Dust", 2),
        ("Fire", "Energy", 2),
        ("Water", "Life", 1),
        ("Energy", "Life", 3),
        ("Life", "Human", 2),
        ("Life", "Animal", 2),
        ("Animal", "Bird", 1),
        ("Wind", "Bird", 1),
        ("Rain", "Plant", 2),
        ("Cloud", "Forest", 1),
        ("Dust", "Earth", 1),
        ("Human", "Tree", 1),
        ("Bird", "Seed", 1),
        ("Forest", "Life", 1),
        ("Plant", "Life", 1),
        ("Animal", "Human", 1),
    ]

    for source, target, weight in weighted_edges:
        graph.add_edge(source, target, weight=weight)

    return graph


def build_threshold_graph() -> nx.DiGraph:
    """Build a compact directed weighted graph suited for threshold clustering."""
    graph = nx.DiGraph()
    for node in range(8):
        graph.add_edge(node, (node + 1) % 8, weight=1.0)
        graph.add_edge(node, (node + 2) % 8, weight=2.0)
    return graph


def build_algorithm_graph(algorithm_name: str) -> nx.Graph | nx.DiGraph:
    """Pick a graph variant that matches the algorithm expectations better."""
    if algorithm_name == "lswl_plus":
        return nx.karate_club_graph()
    if algorithm_name == "threshold_clustering":
        return build_threshold_graph()
    return build_demo_graph()


def build_algorithm_kwargs(algorithm_name: str) -> dict[str, Any]:
    """Provide minimal required parameters for algorithms that need them."""
    parameter_map: dict[str, dict[str, Any]] = {
        "girvan_newman": {"level": 2},
        "em": {"k": 3},
        "scan": {"epsilon": 0.7, "mu": 2},
        "gdmp2": {"min_threshold": 0.5},
        "spinglass": {"spins": 6},
        "agdl": {"number_communities": 3, "kc": 2},
        "louvain": {"resolution": 1.0, "randomize": False},
        "leiden": {"initial_membership": None},
        "rb_pots": {"resolution_parameter": 1.0},
        "rber_pots": {"resolution_parameter": 1.0},
        "cpm": {"resolution_parameter": 0.5},
        "async_fluid": {"k": 3},
        "der": {"walk_len": 3, "threshold": 0.0001},
        "belief": {"max_it": 20},
        "threshold_clustering": {"threshold_function": lambda ties: sum(ties) / len(ties)},
        "lswl": {"query_node": "Life"},
        "mod_m": {"query_node": "Life"},
        "mod_r": {"query_node": "Life"},
        "head_tail": {"head_tail_ratio": 0.4},
        "kcut": {"kmax": 3},
        "spectral": {"kmax": 3},
        "r_spectral_clustering": {"n_clusters": 3},
    }
    return parameter_map.get(algorithm_name, {})


def run_infomap_direct(graph: nx.DiGraph) -> dict[str, Any]:
    """Run Infomap through the native package instead of the CDlib wrapper."""
    import infomap

    node_names = list(graph.nodes())
    node_to_id = {name: index for index, name in enumerate(node_names)}
    id_to_node = {index: name for name, index in node_to_id.items()}

    runner = infomap.Infomap("--directed --silent")
    runner.add_nodes(id_to_node)

    for source, target, data in graph.edges(data=True):
        runner.add_link(node_to_id[source], node_to_id[target], data.get("weight", 1.0))

    runner.run()

    communities_by_id: dict[int, list[str]] = {}
    for node in runner.tree:
        if node.is_leaf:
            communities_by_id.setdefault(node.module_id, []).append(id_to_node[node.node_id])

    communities = [sorted(nodes) for _community_id, nodes in sorted(communities_by_id.items())]
    community_sizes = [len(nodes) for nodes in communities]
    return {
        "method_name": "Infomap",
        "community_count": len(communities),
        "community_sizes": community_sizes,
        "communities": communities,
    }


def run_one_algorithm(algorithm_name: str) -> bool:
    """Run one algorithm and print a compact result or error."""
    graph = build_algorithm_graph(algorithm_name)
    kwargs = build_algorithm_kwargs(algorithm_name)

    try:
        if algorithm_name == "infomap":
            summary = run_infomap_direct(graph)
        else:
            result = run_mono_community_algorithm(graph, algorithm_name, **kwargs)
            summary = summarize_mono_community_result(result)
        print(f"[OK] {algorithm_name}")
        print(f"  method_name: {summary['method_name']}")
        print(f"  communities: {summary['community_count']}")
        print(f"  sizes: {summary['community_sizes']}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {algorithm_name}: {type(exc).__name__}: {exc}")
        return False


def main() -> None:
    """Parse arguments and run one or all crisp mono algorithms."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--algorithm",
        help="Run only one algorithm by key. Default: run all listed mono crisp algorithms.",
    )
    args = parser.parse_args()

    if args.algorithm:
        run_one_algorithm(args.algorithm)
        return

    success_count = 0
    error_count = 0
    for algorithm in get_mono_community_algorithm_evaluation():
        algorithm_name = str(algorithm["key"])
        if run_one_algorithm(algorithm_name):
            success_count += 1
        else:
            error_count += 1
    print(f"\nSummary: {success_count} OK, {error_count} errors")


if __name__ == "__main__":
    main()
