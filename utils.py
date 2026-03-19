import random


def are_equal(first: float, second: float, delta: float) -> bool:
    return abs(first - second) < delta


def custom_random(max_value: float) -> float:
    """Рандомное число полуинтервала (0; max_value]"""
    return (1 - random.random()) * max_value