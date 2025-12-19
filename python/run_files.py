import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set


# =========================
# CONFIG
# =========================
INPUT_JSON = "dependencies.json"
BASE_DIR = "scripts"  # folder where your .txt files live


# =========================
# 1) LOAD DEPENDENCIES
# =========================
def load_dependencies(path: str) -> Dict[str, List[str]]:
    """
    Reads dependencies.json and returns dict:
      { "file1.txt": [],
        "file2.txt": ["file1.txt"],
        ...
      }
    """
    with open(path, "r") as f:
        data = json.load(f)

    dep_dict: Dict[str, List[str]] = {}
    for item in data["files"]:
        name = item["name"]
        deps = item.get("depends_on", [])
        dep_dict[name] = deps

    return dep_dict


# =========================
# 2) TOPOLOGICAL SORT (dependency-safe order)
# =========================
def topological_sort(dependencies: Dict[str, List[str]]) -> List[str]:
    """
    dependencies[file] = list of files that this file depends on.
    Returns a list of files in a valid execution order.
    Raises ValueError if there is a cycle.
    """

    # collect all files (keys + deps)
    all_files: Set[str] = set(dependencies.keys())
    for deps in dependencies.values():
        all_files.update(deps)

    # build graph: dep -> dependent
    graph = defaultdict(list)  # dep -> [dependents]
    in_degree = {f: 0 for f in all_files}

    for file, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(file)
            in_degree[file] += 1

    # start with nodes that have in_degree 0
    queue = deque([f for f in all_files if in_degree[f] == 0])

    order: List[str] = []
    while queue:
        current = queue.popleft()
        order.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(all_files):
        raise ValueError(
            "Cycle detected in dependencies. No valid execution order.")

    return order


# =========================
# 3) REQUIRED SET FOR A TARGET FILE
# =========================
def collect_all_prerequisites(dependencies: Dict[str, List[str]], target: str) -> Set[str]:
    """
    Returns all files that must run before target (recursive).
    """
    visited: Set[str] = set()

    def dfs(file: str):
        for dep in dependencies.get(file, []):
            if dep not in visited:
                visited.add(dep)
                dfs(dep)

    dfs(target)
    return visited


def execution_order_for_target(dependencies: Dict[str, List[str]], target: str) -> List[str]:
    """
    Returns a dependency-safe order for only:
      prerequisites(target) + target
    """
    all_files = set(dependencies.keys()) | {
        d for deps in dependencies.values() for d in deps}
    if target not in all_files:
        raise ValueError(
            f"Target file '{target}' is not defined in dependencies.json")

    global_order = topological_sort(dependencies)
    prereqs = collect_all_prerequisites(dependencies, target)
    required = prereqs | {target}

    return [f for f in global_order if f in required]


# =========================
# 4) GROUPING (for DISPLAY)
# =========================
def group_by_dependency_count(files_subset: List[str], dependencies: Dict[str, List[str]]) -> Dict[int, List[str]]:
    """
    Groups by number of DIRECT dependencies (depends_on length):
      Group 1: 0 deps
      Group 2: 1 dep
      Group 3: >1 deps
    """
    g1, g2, g3 = [], [], []

    for f in files_subset:
        deps = dependencies.get(f, [])
        if len(deps) == 0:
            g1.append(f)
        elif len(deps) == 1:
            g2.append(f)
        else:
            g3.append(f)

    return {1: g1, 2: g2, 3: g3}


def print_groups(groups_dict: Dict[int, List[str]], title: str):
    print(f"\n{title}")
    print(f"Group 1 (independent files): {groups_dict[1]}")
    print(f"Group 2 (exactly 1 dependency): {groups_dict[2]}")
    print(f"Group 3 (more than 1 dependency): {groups_dict[3]}")


def target_group(dependencies: Dict[str, List[str]], target: str) -> int:
    deps = dependencies.get(target, [])
    if len(deps) == 0:
        return 1
    if len(deps) == 1:
        return 2
    return 3


# =========================
# 5) RUNNER (prototype)
# =========================
def run_file(path: Path):
    """
    Prototype "run": print file name and contents.
    Replace this later with real execution.
    """
    print(f"\n=== RUNNING {path.name} ===")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text()
    print(content if content.strip() else "[File is empty]")


# =========================
# 6) CASE 1: RUN ALL
# =========================
def run_all_files():
    dependencies = load_dependencies(INPUT_JSON)

    # Grouped view (display)
    all_files = list(dependencies.keys())
    grouped = group_by_dependency_count(all_files, dependencies)
    print_groups(
        grouped, "Case 1: Run ALL files (grouped by dependency count)")

    # Dependency-safe execution order
    order = topological_sort(dependencies)
    print("\nExecution order (dependency-safe):")
    for f in order:
        print("  -", f)

    # Run
    base = Path(BASE_DIR)
    print("\nStarting execution...")
    for f in order:
        run_file(base / f)


# =========================
# 7) CASE 2: RUN ONE FILE
# =========================
def run_single_file_with_deps(target: str):
    dependencies = load_dependencies(INPUT_JSON)

    print(f"\nCase 2: Run ONE file: {target}")
    print(f"Direct dependencies of {target}: {dependencies.get(target, [])}")
    print(f"{target} belongs to Group {target_group(dependencies, target)} (direct dependency count).")

    # Required set + correct order
    order = execution_order_for_target(dependencies, target)

    # Grouped view for only required files
    grouped_required = group_by_dependency_count(order, dependencies)
    print_groups(grouped_required, f"Required files to run {target} (grouped)")

    print("\nExecution order (dependency-safe for required files):")
    for f in order:
        print("  -", f)

    # Run
    base = Path(BASE_DIR)
    print("\nStarting execution...")
    for f in order:
        run_file(base / f)


# =========================
# MAIN - choose what you want
# =========================
if __name__ == "__main__":

    # ---- OPTION A: RUN ALL FILES ----
    # run_all_files()

    # ---- OPTION B: RUN ONE FILE + ITS DEPENDENCIES ----
    run_single_file_with_deps("file7.txt")
