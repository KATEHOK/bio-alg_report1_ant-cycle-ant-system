import time
from ant_system import AntSystem
from graph import Graph, Edge, path_len


def report_example():
    """Экспериментальный запуск примера из отчета (пункт 2)"""
    start_time = time.time()
    print("Running: report example")
    graph = Graph(nodes_number=4, extra_edges_number=0, max_pheromone=0.1, max_distance=3, seed=2026)
    graph.set_edge(
        src=0, dst=1, edge=Edge(src=0, dst=1, size=1, pheromone=0.1, random_size=False, random_pheromone=False)
    )
    graph.set_edge(
        src=0, dst=2, edge=Edge(src=0, dst=2, size=3, pheromone=0.1, random_size=False, random_pheromone=False)
    )
    graph.set_edge(
        src=0, dst=3, edge=None
    )
    graph.set_edge(
        src=1, dst=2, edge=Edge(src=1, dst=2, size=2, pheromone=0.1, random_size=False, random_pheromone=False)
    )
    graph.set_edge(
        src=1, dst=3, edge=Edge(src=1, dst=3, size=2, pheromone=0.1, random_size=False, random_pheromone=False)
    )
    graph.set_edge(
        src=2, dst=3, edge=Edge(src=2, dst=3, size=1, pheromone=0.1, random_size=False, random_pheromone=False)
    )
    ant_system = AntSystem(alpha=1, beta=2, ro=0.1, q=100, ants_number=2, max_init_pheromone=0.1)
    iterations, duration, global_best, local_best, paths = ant_system.search_path(
        start=0, goal=3, graph=graph,
        max_iteration=100, max_same_results_number=1,
        reinit_pheromones=False, seed=2026, save_all_paths=True
    )
    print(
        "Small graph",
        f"Iterations: {iterations}",
        f"Duration: {duration}",
        f"Global best path len: {path_len(global_best)}",
        f"Local best path len: {path_len(local_best)}",
        sep="\n\t",
    )
    for iteration_id, iteration in enumerate(paths):
        for ant_id, (path, result) in enumerate(iteration):
            print(
                iteration_id, ant_id, result,
                [0] + [edge.dst for edge in path],
                sep="\t"
            )
    print(f"Total time: {time.time() - start_time}")


def random_graph_and_system():
    start_time = time.time()
    print("Running: random graph and system")

    seed = 2026
    nodes_number = 48
    extra_edges_number = (nodes_number - 1) * (nodes_number - 2) // 4
    max_distance = nodes_number / 2

    start = 0
    goal = 3 * nodes_number // 4

    max_iterations = nodes_number * 100
    max_sames = 3

    reinit_pheromones = True
    result_cmp_delta = 0.000_000_001
    path_len_precision = 9
    save_all_paths = False

    out_dir = "../out/"

    alpha = 1.5
    beta = 1.5
    ro = 0.1
    q = 10
    ants_number = nodes_number // 4
    max_init_pheromone = 0.1

    graph = Graph(nodes_number, extra_edges_number, max_init_pheromone, max_distance, seed)
    print("Inited: graph")
    ant_system = AntSystem(alpha, beta, ro, q, ants_number, max_init_pheromone)
    print("Inited: ant system")

    filename = out_dir + "by-alpha.txt"
    with open(filename, "w") as file:
        for alpha in range(20):
            alpha = (alpha + 1) / 10
            ant_system.alpha = alpha
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(alpha),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.alpha = alpha
    print(f"Test result has whitten: {filename}")

    filename = out_dir + "by-beta.txt"
    with open(filename, "w") as file:
        for beta in range(20):
            beta = (beta + 1) / 10
            ant_system.beta = beta
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(beta),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.beta = beta
    print(f"Test result has whitten: {filename}")

    filename = out_dir + "by-ro.txt"
    with open(filename, "w") as file:
        for ro in range(20):
            ro = (ro + 1) / 50
            ant_system.ro = ro
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(ro),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.ro = ro
    print(f"Test result has whitten: {filename}")

    filename = out_dir + "by-q.txt"
    with open(filename, "w") as file:
        for q in range(20):
            q += 1
            ant_system.q = q
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(q),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.q = q
    print(f"Test result has whitten: {filename}")

    filename = out_dir + "by-ants_number.txt"
    with open(filename, "w") as file:
        for ants_number in range(20):
            ants_number = (ants_number + 1) * round(nodes_number / 20)
            ant_system.ants_number = ants_number
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(ants_number),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.ants_number = ants_number
    print(f"Test result has whitten: {filename}")

    filename = out_dir + "by-max_init_pheromone.txt"
    with open(filename, "w") as file:
        for max_init_pheromone in range(20):
            max_init_pheromone = (max_init_pheromone + 1) / 10
            ant_system.max_init_pheromone = max_init_pheromone
            iterations, time_duration, global_best_path, _, _ = ant_system.search_path(
                start, goal, graph, max_iterations, max_sames,
                reinit_pheromones, result_cmp_delta, seed, path_len_precision, save_all_paths
            )
            file.write("\t".join((
                str(max_init_pheromone),
                str(iterations),
                str(round(time_duration, path_len_precision)),
                str(round(path_len(global_best_path), path_len_precision)),
            )) + "\n")
        ant_system.max_init_pheromone = max_init_pheromone
    print(f"Test result has whitten: {filename}")
    print(f"Total time: {time.time() - start_time}")


if __name__ == "__main__":
    report_example()
    random_graph_and_system()
