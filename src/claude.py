import numpy as np
from typing import List, Tuple, Set, Dict, Optional
from enum import Enum
import random
import os

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

class BattleshipAI:
    def __init__(self, board_size: int = 10):
        self.board_size = board_size
        self.probability_map = np.ones((board_size, board_size))
        self.hits = set()
        self.misses = set()
        self.ships = {
            'Carrier': 5,
            'Battleship': 4,
            'Cruiser': 3,
            'Submarine': 3,
            'Destroyer': 2
        }
        self.remaining_ships = self.ships.copy()
        self.hunt_stack = []
        self.last_hits = []
        self.confirmed_ship_cells = set()
        self.unconfirmed_hits = set()  # New: track hits that aren't part of a sunk ship
        self.sunk_ship_positions = set()  # New: track positions of sunk ships
        self.min_remaining_ship_size = min(self.ships.values())  # New: track smallest remaining ship
        self.max_remaining_ship_size = max(self.ships.values())  # New: track largest remaining ship

    def is_late_game(self) -> bool:
        """Check if we're in late game (less than 3 ships remaining)"""
        return len(self.remaining_ships) <= 2

    def calculate_ship_density(self, x: int, y: int) -> float:
        """Calculate how many different ways ships can be placed over this cell"""
        density = 0
        for ship_length in self.remaining_ships.values():
            # Check horizontal placement
            for start_y in range(max(0, y - ship_length + 1), min(y + 1, self.board_size - ship_length + 1)):
                positions = [(x, start_y + i) for i in range(ship_length)]
                if self.is_valid_ship_placement(positions):
                    density += 1

            # Check vertical placement
            for start_x in range(max(0, x - ship_length + 1), min(x + 1, self.board_size - ship_length + 1)):
                positions = [(start_x + i, y) for i in range(ship_length)]
                if self.is_valid_ship_placement(positions):
                    density += 1
                    
        return density

    def is_valid_ship_placement(self, positions: List[Tuple[int, int]]) -> bool:
        """Check if a ship placement is valid given current game state"""
        for x, y in positions:
            # Check if position is within bounds
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
            
            # Check if position overlaps with misses or sunk ships
            if (x, y) in self.misses or (x, y) in self.sunk_ship_positions:
                return False
            
            # Check if position is adjacent to a sunk ship
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                adj_x, adj_y = x + dx, y + dy
                if (adj_x, adj_y) in self.sunk_ship_positions:
                    return False

        # Check if placement is consistent with unconfirmed hits
        hits_in_placement = sum(1 for pos in positions if pos in self.unconfirmed_hits)
        return hits_in_placement == len(set(positions) & self.unconfirmed_hits)

    def update_late_game_probabilities(self):
        """Update probability map with late game specific strategies"""
        # Reset probability map
        self.probability_map = np.zeros((self.board_size, self.board_size))
        
        # Calculate base probabilities using ship density
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i, j) not in self.hits and (i, j) not in self.misses:
                    self.probability_map[i, j] = self.calculate_ship_density(i, j)

        # Adjust probabilities based on unconfirmed hits
        if self.unconfirmed_hits:
            for hit_x, hit_y in self.unconfirmed_hits:
                # Increase probabilities in line with unconfirmed hits
                for ship_length in self.remaining_ships.values():
                    # Check horizontal
                    for y in range(max(0, hit_y - ship_length + 1), min(hit_y + ship_length, self.board_size)):
                        if (hit_x, y) not in self.hits and (hit_x, y) not in self.misses:
                            self.probability_map[hit_x, y] *= 2

                    # Check vertical
                    for x in range(max(0, hit_x - ship_length + 1), min(hit_x + ship_length, self.board_size)):
                        if (x, hit_y) not in self.hits and (x, hit_y) not in self.misses:
                            self.probability_map[x, hit_y] *= 2

        # Consider minimum remaining ship size
        invalid_positions = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i, j) not in self.hits and (i, j) not in self.misses:
                    # Check if any remaining ship can fit here
                    can_fit_ship = False
                    for ship_length in self.remaining_ships.values():
                        # Check horizontal fit
                        horizontal_space = self.get_available_space(i, j, True)
                        # Check vertical fit
                        vertical_space = self.get_available_space(i, j, False)
                        if horizontal_space >= ship_length or vertical_space >= ship_length:
                            can_fit_ship = True
                            break
                    
                    if not can_fit_ship:
                        invalid_positions.add((i, j))
                        self.probability_map[i, j] = 0

    def get_available_space(self, x: int, y: int, horizontal: bool) -> int:
        """Calculate available space in a direction from a position"""
        space = 0
        if horizontal:
            for dy in range(self.board_size - y):
                if (x, y + dy) in self.misses or (x, y + dy) in self.sunk_ship_positions:
                    break
                space += 1
        else:
            for dx in range(self.board_size - x):
                if (x + dx, y) in self.misses or (x + dx, y) in self.sunk_ship_positions:
                    break
                space += 1
        return space

    def update_game_state(self, x: int, y: int, is_hit: bool, hit_ship: Optional[Ship] = None):
        """Update game state with enhanced tracking"""
        if is_hit:
            self.hits.add((x, y))
            self.unconfirmed_hits.add((x, y))
            self.last_hits.append((x, y))
            
            # If a ship was sunk
            if hit_ship and hit_ship.is_sunk():
                # Remove ship from remaining ships
                for ship_name, length in list(self.remaining_ships.items()):
                    if length == len(hit_ship.positions):
                        del self.remaining_ships[ship_name]
                        break
                
                # Update ship position tracking
                self.sunk_ship_positions.update(hit_ship.positions)
                self.unconfirmed_hits -= set(hit_ship.positions)
                
                # Update min/max remaining ship sizes
                if self.remaining_ships:
                    self.min_remaining_ship_size = min(self.remaining_ships.values())
                    self.max_remaining_ship_size = max(self.remaining_ships.values())
                
                # Reset hunting mode
                self.hunt_stack = []
                self.last_hits = []
            else:
                # Add adjacent cells to hunt stack if not already targeted
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.board_size and 
                        0 <= new_y < self.board_size and 
                        (new_x, new_y) not in self.hits and 
                        (new_x, new_y) not in self.misses):
                        self.hunt_stack.append((new_x, new_y))
        else:
            self.misses.add((x, y))

    def get_next_target(self) -> Tuple[int, int]:
        """Get next target with improved late game strategy"""
        def is_valid_target(x: int, y: int) -> bool:
            return (0 <= x < self.board_size and 
                    0 <= y < self.board_size and 
                    (x, y) not in self.hits and 
                    (x, y) not in self.misses)

        # Process hunt stack first
        while self.hunt_stack:
            next_target = self.hunt_stack.pop()
            if is_valid_target(*next_target):
                return next_target

        # Use late game strategy if applicable
        if self.is_late_game():
            self.update_late_game_probabilities()
        else:
            self.update_probability_map()

        # Get valid candidates with highest probability
        max_prob = np.max(self.probability_map)
        if max_prob > 0:
            candidates = [(i, j) for i, j in zip(*np.where(self.probability_map == max_prob))
                         if is_valid_target(i, j)]
            if candidates:
                return random.choice(candidates)

        # Fallback: get any remaining valid target
        valid_targets = [(i, j) for i in range(self.board_size) 
                        for j in range(self.board_size) 
                        if is_valid_target(i, j)]
        
        if valid_targets:
            return random.choice(valid_targets)
        
        raise ValueError("No valid targets remaining")
        
    def _get_parity_cells(self) -> List[Tuple[int, int]]:
        """Trả về các ô theo mẫu bàn cờ"""
        cells = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i + j) % 2 == (1 if self.parity else 0):
                    if (i, j) not in self.hits and (i, j) not in self.misses:
                        cells.append((i, j))
        return cells
    
    def _can_fit_smallest_ship(self, x: int, y: int) -> bool:
        """Kiểm tra xem ô có thể chứa tàu nhỏ nhất không"""
        min_ship_size = min(self.remaining_ships.values()) if self.remaining_ships else 2
        
        # Kiểm tra theo chiều ngang
        horizontal_space = 0
        for j in range(max(0, y - min_ship_size + 1), min(self.board_size, y + min_ship_size)):
            if (x, j) not in self.misses and (x, j) not in self.hits:
                horizontal_space += 1
            else:
                horizontal_space = 0
            if horizontal_space >= min_ship_size:
                return True

        # Kiểm tra theo chiều dọc
        vertical_space = 0
        for i in range(max(0, x - min_ship_size + 1), min(self.board_size, x + min_ship_size)):
            if (i, y) not in self.misses and (i, y) not in self.hits:
                vertical_space += 1
            else:
                vertical_space = 0
            if vertical_space >= min_ship_size:
                return True

        return False

    def _calculate_ship_probability(self, ship_length: int) -> np.ndarray:
        """Tính xác suất có thể đặt tàu với độ dài cho trước"""
        prob_map = np.zeros((self.board_size, self.board_size))
        
        # Xét các vị trí có thể đặt tàu
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Kiểm tra theo chiều ngang
                if j + ship_length <= self.board_size:
                    valid = True
                    has_hit = False
                    cells = [(i, j+k) for k in range(ship_length)]
                    
                    for x, y in cells:
                        if (x, y) in self.misses or (x, y) in self.confirmed_ship_cells:
                            valid = False
                            break
                        if (x, y) in self.hits:
                            has_hit = True
                    
                    # Tăng xác suất nếu có hit gần đó
                    multiplier = 3 if has_hit else 1
                    if valid:
                        for x, y in cells:
                            prob_map[x][y] += multiplier
                
                # Kiểm tra theo chiều dọc
                if i + ship_length <= self.board_size:
                    valid = True
                    has_hit = False
                    cells = [(i+k, j) for k in range(ship_length)]
                    
                    for x, y in cells:
                        if (x, y) in self.misses or (x, y) in self.confirmed_ship_cells:
                            valid = False
                            break
                        if (x, y) in self.hits:
                            has_hit = True
                    
                    multiplier = 3 if has_hit else 1
                    if valid:
                        for x, y in cells:
                            prob_map[x][y] += multiplier
        
        return prob_map

    def update_probability_map(self):
        """Cập nhật bản đồ xác suất dựa trên các hits và misses hiện tại"""
        self.probability_map = np.zeros((self.board_size, self.board_size))
        
        # Chỉ tính xác suất cho các tàu còn lại
        for ship_name, ship_length in self.remaining_ships.items():
            ship_probability = self._calculate_ship_probability(ship_length)
            self.probability_map += ship_probability
        
        # Áp dụng các ràng buộc bổ sung
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i, j) in self.hits or (i, j) in self.misses:
                    self.probability_map[i][j] = 0
                elif not self._can_fit_smallest_ship(i, j):
                    self.probability_map[i][j] = 0
        
        # Normalize probability map
        total = np.sum(self.probability_map)
        if total > 0:
            self.probability_map /= total

    def _get_adjacent_cells(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Trả về các ô liền kề hợp lệ"""
        adjacent = []
        if self.hunting_direction:
            dx, dy = self.hunting_direction.value
            next_x, next_y = x + dx, y + dy
            if (0 <= next_x < self.board_size and 
                0 <= next_y < self.board_size and 
                (next_x, next_y) not in self.hits and 
                (next_x, next_y) not in self.misses):
                adjacent.append((next_x, next_y))
        else:
            for direction in Direction:
                dx, dy = direction.value
                next_x, next_y = x + dx, y + dy
                if (0 <= next_x < self.board_size and 
                    0 <= next_y < self.board_size and 
                    (next_x, next_y) not in self.hits and 
                    (next_x, next_y) not in self.misses):
                    adjacent.append((next_x, next_y))
        return adjacent

    def _find_ship_length(self, x: int, y: int) -> int:
        """Tìm độ dài của tàu đã bị bắn trúng"""
        connected_hits = {(x, y)}
        stack = [(x, y)]
        
        while stack:
            current_x, current_y = stack.pop()
            for next_x, next_y in self._get_adjacent_cells(current_x, current_y):
                if (next_x, next_y) in self.hits and (next_x, next_y) not in connected_hits:
                    connected_hits.add((next_x, next_y))
                    stack.append((next_x, next_y))
        
        return len(connected_hits)

    def play_game(self) -> List[Tuple[int, int, bool]]:
        """Mô phỏng một ván game hoàn chỉnh"""
        moves = []
        while len(moves) < self.board_size * self.board_size:
            x, y = self.get_next_target()
            is_hit = random.random() < 0.3  # 30% cơ hội trúng
            self.update_game_state(x, y, is_hit)
            moves.append((x, y, is_hit))
            if len(self.hits) >= sum(self.ships.values()):
                break
        return moves
    
    def play_complete_game(self) -> List[Tuple[int, int, bool]]:
        """Chơi một ván game hoàn chỉnh và ghi log"""
        game = BattleshipGame()
        moves = []
        
        with open("moves.txt", "w", encoding="utf-8") as f:
            f.write("Initial board:\n")
            f.write(game.get_board_display(show_ships=True))
            f.write("\nShips placement:\n")
            for ship in game.ships:
                f.write(f"{ship.name}: {ship.positions}\n")
            f.write("\nMoves:\n")
            f.write("Move  Position  Result  Board State\n")
            f.write("-" * 50 + "\n")
            
            move_count = 0
            while move_count < self.board_size * self.board_size:
                move_count += 1
                x, y = self.get_next_target()
                is_hit = game.check_hit(x, y)
                
                # Find the hit ship if it's a hit
                hit_ship = None
                if is_hit:
                    for ship in game.ships:
                        if (x, y) in ship.positions:
                            ship.hits.add((x, y))
                            hit_ship = ship
                            break
                
                # Update AI's game state with the hit ship information
                self.update_game_state(x, y, is_hit, hit_ship)  # Pass hit_ship to update_game_state
                moves.append((x, y, is_hit))
                
                # Log move information
                f.write(f"{move_count:4d}  ({x},{y})    {'Hit' if is_hit else 'Miss'}    ")
                f.write(f"Is late game: {self.is_late_game()} {self.remaining_ships}")
                
                # Create current board state
                current_board = np.full((self.board_size, self.board_size), '-')
                for hit_x, hit_y in self.hits:
                    current_board[hit_x][hit_y] = 'H'
                for miss_x, miss_y in self.misses:
                    current_board[miss_x][miss_y] = 'M'
                
                # Print board state
                f.write("\n")
                f.write("   " + " ".join(str(i) for i in range(self.board_size)) + "\n")
                for i in range(self.board_size):
                    f.write(f"{i:2}|")
                    for j in range(self.board_size):
                        f.write(current_board[i][j] + " ")
                    f.write("\n")
                f.write("-" * 50 + "\n")
                
                # Check if all ships are sunk
                if all(ship.is_sunk() for ship in game.ships):
                    break
            
            # Game summary
            f.write("\nGame Summary:\n")
            f.write(f"Total moves: {move_count}\n")
            f.write(f"Total hits: {len(self.hits)}\n")
            f.write(f"Total misses: {len(self.misses)}\n")
            f.write(f"Hit ratio: {len(self.hits)/move_count:.2%}\n")
            
            f.write("\nFinal ship status:\n")
            for ship in game.ships:
                f.write(f"{ship.name}: {'SUNK' if ship.is_sunk() else 'FLOATING'}\n")
                f.write(f"Positions: {ship.positions}\n")
                f.write(f"Hits: {ship.hits}\n")
        
        return moves


def runBatch(batchNum):
    total_moves = 0

    for i in range(batchNum):
        ai = BattleshipAI()
        print("Starting new game...")
        print("\nInitial board:")
        game = BattleshipGame()
        print(game.get_board_display(show_ships=True))
        print("\nPlaying game...")
        moves = ai.play_complete_game()
        
        print(f"\nGame completed in {len(moves)} moves!")
        total_moves += len(moves)
        print("Check moves.txt for detailed game log.")
    print(total_moves / batchNum)

if __name__ == "__main__":
    batchNum = 1
    runBatch(batchNum)