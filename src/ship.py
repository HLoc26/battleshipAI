from typing import List, Tuple
from enum import Enum

class Direction(Enum):
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    EAST = (0, 1)
    WEST = (0, -1)

class Ship:
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length
        self.positions: List[Tuple[int, int]] = []
        self.hits = set()

    def is_sunk(self) -> bool:
        return len(self.hits) == self.length
    def __str__(self):
        return f"{self.name} ({self.length})"