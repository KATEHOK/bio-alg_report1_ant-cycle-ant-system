import random
import time
from graph import Graph, Edge
from utils import are_equal


class AntSystem:
    """Модификация муравьиной системы: Ant-cycle AS"""

    alpha: float                # степень влияния феромона (0 - не влияет)
    beta: float                 # степень влияния эвристики (0 - не влияет)
    ro: float                   # скорость испарения феромона (0 - без испарения; 1 - мгновенное испарение)
    q: float                    # константа пропорциональности добавления феромона
    ants_number: int            # количество муравьев
    max_init_pheromone: float   # ограничение начального количества феромона

    def __init__(self,
        alpha: float,
        beta: float,
        ro: float,
        q: float,
        ants_number: int,
        max_init_pheromone: float,
    ):
        self.alpha = alpha
        self.beta = beta
        self.ro = ro
        self.q = q
        self.ants_number = ants_number
        self.max_init_pheromone = max_init_pheromone

    def search_path(self,
            start: int,
            goal: int,
            graph: Graph,
            max_iteration: int,
            max_same_results_number: int,
            results_cmp_delta: float = 0.000_000_001,
            seed: float | int | None = None,
            path_len_precision: int = 9
        ) -> tuple[int, float, list[Edge], list[Edge]]:
        """Вернет: количество итераций, время работы, лучшие пути за все и за последнюю итерацию"""
        random.seed(seed)

        graph.set_random_pheromones(self.max_init_pheromone)
        iteration_id = 0
        same_results_counter = 0

        global_best_path: list[Edge] = []
        global_best_path_len: float = 0
        local_best_path: list[Edge] = []
        local_best_path_len: float = 0

        time_start = time.time()

        while iteration_id < max_iteration and same_results_counter < max_same_results_number:
            # запуск муравьев
            (
                visited_edges_counter,
                local_best_path,
                local_best_path_len
            ) = self.run_ants(graph, start, goal, path_len_precision)

            # испарение феромона
            self.evaporate_pheromone(graph)

            # добавление феромона для посещенных вершин
            self.top_up_pheromone(visited_edges_counter)

            # найдено глобально лучшее решение
            if global_best_path_len == 0 or 0 < local_best_path_len < global_best_path_len:
                global_best_path = local_best_path
                global_best_path_len = local_best_path_len
                same_results_counter = 0

            # найден эквивалент лучшего решения
            elif are_equal(global_best_path_len, local_best_path_len, results_cmp_delta):
                same_results_counter += 1

            else:
                same_results_counter = 0
            iteration_id += 1

        duration = time.time() - time_start
        return iteration_id, duration, global_best_path, local_best_path

    def run_ants(
        self, graph: Graph, start_node: int, goal_node: int, path_len_precision: int
    ) -> tuple[
        dict[Edge, dict[float, int]],
        list[Edge],
        float
    ]:
        visited_edges_counter: dict[Edge, dict[float, int]] = {}    # {edge: {path_len: amount, ...}, ...}
        local_best_path = []
        local_best_path_len = 0

        for ant in range(self.ants_number):
            ant_path: list[Edge] = []
            ant_path_len: float = 0
            tabu_list: set[int] = set()
            cur_node: int = start_node

            # поиск пути муравьем ant
            while cur_node != goal_node:
                next_node = self.choose_next_node(graph, cur_node, tabu_list)
                if next_node is None:  # тупик
                    ant_path = []
                    ant_path_len = 0
                    break
                edge = graph.get_edge(cur_node, next_node)
                ant_path.append(edge)
                ant_path_len += edge.size
                tabu_list.add(cur_node)
                cur_node = next_node

            # обновляем счетчик посещений ребра при прохождении путями такой же длины
            else:
                ant_path_len = round(ant_path_len, path_len_precision)
                for edge in ant_path:
                    visited_edges_counter[edge] = visited_edges_counter.get(edge, {})
                    visited_edges_counter[edge][ant_path_len] = visited_edges_counter[edge].get(
                        ant_path_len, 0
                    ) + 1

            # лучший на итерации?
            if local_best_path_len == 0 or 0 < ant_path_len < local_best_path_len:
                local_best_path = ant_path
                local_best_path_len = ant_path_len
        return visited_edges_counter, local_best_path, local_best_path_len

    def choose_next_node(self, graph: Graph, cur: int, tabu_list: set[int]) -> int | None:
        candidates: dict[Edge, dict[str, float]] = {}
        total_attractiveness = 0
        # кандидаты, их привлекательность
        for edge in graph.get_edges(cur):
            if edge.get_another_node(cur) not in tabu_list:
                candidates[edge] = {
                    "attractiveness": edge.pheromone ** self.alpha * edge.size ** -self.beta
                }
                total_attractiveness += candidates[edge]["attractiveness"]
        if len(candidates) == 0:   # кандидатов нет (тупик)
            return None
        # вероятности выбора кандидатов
        for edge_params in candidates.values():
            edge_params["probability"] = edge_params["attractiveness"] / total_attractiveness
        # выборы (сектора колеса пропорциональны вероятностям)
        random_value = random.random()
        last_edge = None
        for edge, params in candidates.items():
            if random_value < params["probability"]:
                return edge.get_another_node(cur)
            random_value -= params["probability"]
            last_edge = edge
        return last_edge.get_another_node(cur)

    def evaporate_pheromone(self, graph: Graph):
        graph.foreach_edge(lambda edge: edge.evaporate_pheromone(self.ro))

    def top_up_pheromone(self, visited_edges_counter: dict[Edge, dict[float, int]]):
        for edge, counter in visited_edges_counter.items():
            for path_len, amount in counter.items():
                edge.pheromone += amount * self.q / path_len
