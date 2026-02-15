"""
Entry point for the submission format: runs the adaptive solver and returns
the solution in the format required by the guidelines: a list of tuples
(node_id, gold_amount) for each stop, with every consecutive pair connected
in the graph. Path ends with (0, 0).
"""

import networkx as nx

from src.gold_collection.solvers.adaptive_solver import solve_return_solution


def is_valid(problem, path) -> bool:
    """
    Check that the path is admissible: depot is adjacent to the first node,
    and every consecutive pair (n1, n2) is connected by an edge.

    (Definition agreed with professor: explicit check for edge 0 -> path[0][0],
    and has_edge for each consecutive pair; no yield, return bool.)
    """
    if not path:
        return False
    G = problem.graph
    if path[0][0] != 0 and not G.has_edge(0, path[0][0]):
        return False
    for (n1, _), (n2, _) in zip(path, path[1:]):
        if not G.has_edge(n1, n2):
            return False
    return True


def _expand_path(problem, stops: list, pickups: list) -> list:
    """
    Expand logical stops into a full path where every consecutive pair
    is connected (shortest path). Returns list of (node_id, gold_amount).
    """
    G = problem.graph
    weight = "dist"
    out = []
    for i in range(len(stops) - 1):
        a, b = stops[i], stops[i + 1]
        gold_a, gold_b = pickups[i], pickups[i + 1]
        try:
            full = nx.shortest_path(G, a, b, weight=weight)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
        if i == 0:
            out.append((full[0], gold_a))
        for j in range(1, len(full)):
            out.append((full[j], gold_b if j == len(full) - 1 else 0.0))
    return out


def _baseline_admissible_path(problem) -> list:
    """
    Build an admissible path: round-trip 0 -> city -> 0 for each city.
    Used as fallback if the solver output is invalid.
    """
    G = problem.graph
    out = [(0, 0.0)]
    for i in range(1, G.number_of_nodes()):
        try:
            path_0_i = nx.shortest_path(G, 0, i, weight="dist")
            path_i_0 = nx.shortest_path(G, i, 0, weight="dist")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
        for j in range(1, len(path_0_i)):
            out.append((path_0_i[j], 0.0))
        out.append((i, float(G.nodes[i].get("gold", 0))))
        for j in range(1, len(path_i_0)):
            out.append((path_i_0[j], 0.0))
    out.append((0, 0.0))
    return out


def run(problem_instance, *, time_budget_s: float = 1200.0, rng_seed=None):
    """
    Run the adaptive solver and return the solution in the guidelines format:
    list of tuples (node_id, gold_amount), with consecutive nodes connected
    in the graph, ending with (0, 0).

    Args:
        problem_instance: Problem instance (from Problem.py).
        time_budget_s: Time budget in seconds.
        rng_seed: Random seed for reproducibility.

    Returns:
        List of (node_id, gold_amount) representing the path and item choices.
    """
    sol = solve_return_solution(
        problem_instance,
        time_budget_s=time_budget_s,
        rng_seed=rng_seed,
    )

    if not sol.trips:
        path = _baseline_admissible_path(problem_instance)
        return path

    path = []
    for trip in sol.trips:
        segment = _expand_path(
            problem_instance,
            list(trip.stops),
            list(trip.pickups),
        )
        if not segment:
            return _baseline_admissible_path(problem_instance)
        path.extend(segment)

    if not path:
        return _baseline_admissible_path(problem_instance)

    # Ensure path ends with (0, 0)
    if path[-1] != (0, 0) and path[-1] != (0, 0.0):
        path.append((0, 0))

    if not is_valid(problem_instance, path):
        path = _baseline_admissible_path(problem_instance)

    return path
