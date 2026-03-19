import random
from typing import Callable
from utils import custom_random


class Edge:
    src: int
    dst: int
    size: float
    pheromone: float

    def __init__(self,
            src: int,
            dst: int,
            size: float,
            pheromone: float,
            random_size: bool = True,
            random_pheromone: bool = True
        ):
        """
        Ребро графа
        :param src: индекс вершины источника
        :param dst: индекс целевой вершины
        :param size: точная или максимальная (если рандом) длина ребра
        :param pheromone: точный или максимальный (если рандом) феромон
        :param random_size: флаг рандомной длины ребра
        :param random_pheromone: флаг рандомного феромона
        """
        self.src = src
        self.dst = dst
        if self.src == self.dst:
            raise ValueError("Loop is restricted!")
        elif size == 0:
            raise ValueError("Zero-len edge is restricted!")
        else:
            self.size = custom_random(size) if random_size else size
            if random_pheromone:
                self.set_random_pheromone(pheromone)
            else:
                self.pheromone = pheromone

    def __eq__(self, other: 'Edge') -> bool:
        """a -> b == b -> a"""
        return any([
            self.src == other.src and self.dst == other.dst,
            self.src == other.dst and self.dst == other.src
        ])

    def __hash__(self) -> tuple[int, int]:
        if self.src <= self.dst:
            return self.src, self.dst
        return self.dst, self.src

    def get_another_node(self, node: int):
        return self.src if self.dst == node else self.dst

    def has(self, node: int) -> bool:
        return self.src == node or self.dst == node

    def evaporate_pheromone(self, ro: float):
        self.pheromone *= (1 - ro)

    def set_random_pheromone(self, max_pheromone: float):
        self.pheromone = custom_random(max_pheromone)


class Graph:
    adj_matrix: list[list[Edge | None]] # матрица смежности

    def __init__(self,
            nodes_number: int,
            extra_edges_number: int,
            max_pheromone: float,
            max_distance: float,
            seed: float | int | None = None
        ):
        """
        Ant-System graph
        :param nodes_number: количество узлов
        :param extra_edges_number: количество ребер сверх базового (nodes_number - 1)
        :param max_pheromone: ограничение начального количества феромона
        :param max_distance: ограничение длины ребра
        :param seed: начальное состояние ГСЧ при создании графа
        """
        self.adj_matrix = [[None for _ in range(nodes_number)] for _ in range(nodes_number)]
        random.seed(seed)

        # связный граф имеет хотя бы (nodes_number - 1) ребер
        for i in range(nodes_number - 1):
            edge = Edge(i, i + 1, max_distance, max_pheromone)
            self.set_edge(i, i + 1, edge)

        # дополнительные ребра
        if extra_edges_number > (nodes_number - 2) * (nodes_number - 1) // 2:
            raise ValueError("Too much edges!")
        while extra_edges_number > 0:
            src = random.randint(0, self.size - 1)
            dst = random.randint(0, self.size - 2)
            if dst >= src:  dst += 1
            if self.get_edge(src, dst) is None:
                edge = Edge(src, dst, max_distance, max_pheromone)
                self.set_edge(src, dst, edge)
                extra_edges_number -= 1

    @property
    def size(self):
        return len(self.adj_matrix)

    def get_edge(self, src: int, dst: int) -> Edge | None:
        """Ребро между узлами (при наличии)"""
        if 0 <= src < self.size and 0 <= dst < self.size:
            return self.adj_matrix[src][dst]
        return None

    def get_edges(self, node: int) -> list[Edge]:
        """Все смежные ребра для вершины"""
        if 0 <= node < self.size:
            return [edge for edge in self.adj_matrix[node] if edge is not None]
        return []

    def set_edge(self,
        src: int,
        dst: int,
        edge: Edge | None
    ):
        if 0 <= src < self.size and 0 <= dst < self.size:
            self.adj_matrix[src][dst] = edge
            self.adj_matrix[dst][src] = edge

    def foreach_edge(self, func: Callable, *args, **kwargs):
        for src in range(self.size - 1):
            for dst in range(src + 1, self.size):
                edge = self.get_edge(src, dst)
                if edge is not None:
                    func(edge, *args, **kwargs)

    def set_random_pheromones(self, max_pheromone: float):
        self.foreach_edge(lambda edge: edge.set_random_pheromone(max_pheromone))


def path_len(path: list[Edge]) -> float:
    res = 0
    for edge in path:
        res += edge.size
    return res
