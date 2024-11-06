import numpy as np
import random
from typing import List, Tuple, Set, Dict, Optional
from ship import Ship

class BattleshipGame:
    def __init__(self, board_size: int = 10):
        self.board_size = board_size
        self.board = np.full((board_size, board_size), ' ')
        self.ships: List[Ship] = []
        self.initialize_ships()
        
    def initialize_ships(self):
        ships_config = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2)
        ]
        
        for ship_name, ship_length in ships_config:
            ship = Ship(ship_name, ship_length)
            while True:
                # Chọn ngẫu nhiên hướng và vị trí
                is_horizontal = random.choice([True, False])
                if is_horizontal:
                    x = random.randint(0, self.board_size - 1)
                    y = random.randint(0, self.board_size - ship_length)
                    positions = [(x, y + i) for i in range(ship_length)]
                else:
                    x = random.randint(0, self.board_size - ship_length)
                    y = random.randint(0, self.board_size - 1)
                    positions = [(x + i, y) for i in range(ship_length)]
                
                # Kiểm tra xem có thể đặt tàu không
                if all(self.board[pos[0]][pos[1]] == ' ' for pos in positions):
                    ship.positions = positions
                    for pos in positions:
                        self.board[pos[0]][pos[1]] = ship_name[0]
                    self.ships.append(ship)
                    break
    
    def check_hit(self, x: int, y: int) -> bool:
        return self.board[x][y] != ' '

    def update_ship_hits(self, x: int, y: int):
        for ship in self.ships:
            if (x, y) in ship.positions:
                ship.hits.add((x, y))
                break

    def get_board_display(self, show_ships: bool = False) -> str:
        """Trả về chuỗi hiển thị bảng game"""
        # Header
        display = "   " + " ".join(str(i) for i in range(self.board_size)) + "\n"
        display += "   " + "-" * (self.board_size * 2 - 1) + "\n"
        
        # Board content
        for i in range(self.board_size):
            display += f"{i:2}|"
            for j in range(self.board_size):
                if show_ships:
                    display += self.board[i][j] + " "
                else:
                    display += "- "
            display += "\n"
        return display
