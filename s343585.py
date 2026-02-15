# Folder: project-work/
# |- src/
# |   |- gold_collection/   (auxiliary code)
# |   |- algorithm.py
# |- Problem.py   (do not modify, from guidelines)
# |- s343585.py

from Problem import Problem
from src.algorithm import run


def solution(p: Problem):
    """
    Solve the Gold Collection Problem for the given instance.

    Args:
        p: Problem instance (from Problem.py).

    Returns:
        List of tuples (node_id, gold_amount) representing the path and
        item choices, ending with (0, 0).
    """
    return run(p)


if __name__ == "__main__":
    prob = Problem(10, alpha=1.0, beta=1.0, density=0.5, seed=42)
    path = solution(prob)
    print(len(path), path[:4], "...", path[-2:] if len(path) >= 2 else path)
