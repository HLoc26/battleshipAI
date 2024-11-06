import numpy as np
import random
from typing import List, Tuple, Set, Dict, Optional
from ship import Ship, Direction

class BattleshipGame:
    SHIPS_CONFIG = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2)
        ]
    def __init__(self, board_size: int = 10):
        self.board_size = board_size
        self.board = np.full((board_size, board_size), ' ')
        self.ships: List[Ship] = []
        self.shots = np.full((board_size, board_size), False)
        self.initialize_ships()

    def initialize_ships(self): 
        for ship_name, ship_length in self.SHIPS_CONFIG:
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

    def place_ships(self):
        """Place all ships randomly on the board"""
        self.board.fill(' ')
        self.ships.clear()
        
        for ship_name, length in self.SHIPS_CONFIG:
            ship = Ship(ship_name, length)
            placed = False
            
            while not placed:
                direction = random.choice(list(Direction))
                if direction == Direction.HORIZONTAL:
                    x = random.randint(0, self.board_size - 1)
                    y = random.randint(0, self.board_size - length)
                    positions = [(x, y + i) for i in range(length)]
                else:  # VERTICAL
                    x = random.randint(0, self.board_size - length)
                    y = random.randint(0, self.board_size - 1)
                    positions = [(x + i, y) for i in range(length)]
                
                # Check if positions are valid
                if self.can_place_ship(positions):
                    ship.positions = positions
                    self.ships.append(ship)
                    # Place ship on board
                    for pos_x, pos_y in positions:
                        self.board[pos_x, pos_y] = ship_name[0]
                    placed = True
    
    def can_place_ship(self, positions: List[Tuple[int, int]]) -> bool:
        """Check if ship can be placed at given positions"""
        for x, y in positions:
            # Check boundaries
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
            # Check if position is empty
            if self.board[x, y] != ' ':
                return False
            # Check surrounding cells (including diagonals)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.board_size and 
                        0 <= new_y < self.board_size and 
                        self.board[new_x, new_y] != ' '):
                        return False
        return True
    
    def fire(self, x: int, y: int) -> Tuple[bool, Optional[Ship]]:
        """Fire at position (x,y). Returns (hit_success, hit_ship)"""
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False, None
        
        if self.shots[x, y]:  # Already fired here
            return False, None
            
        self.shots[x, y] = True
        
        if self.board[x, y] != ' ':
            # Find which ship was hit
            for ship in self.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    return True, ship
        
        return False, None