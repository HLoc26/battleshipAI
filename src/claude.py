import numpy as np
from typing import List, Tuple, Set, Dict
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
        self.hits: Set[Tuple[int, int]] = set()
        self.misses: Set[Tuple[int, int]] = set()
        self.ships = {
            'Carrier': 5,
            'Battleship': 4,
            'Cruiser': 3,
            'Submarine': 3,
            'Destroyer': 2
        }
        self.remaining_ships = self.ships.copy()
        self.hunt_stack: List[Tuple[int, int]] = []
        self.confirmed_ship_cells: Set[Tuple[int, int]] = set()
        self.hunting_direction: Direction = None
        self.parity = True  # Sử dụng chiến lược parity
        
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

    def get_next_target(self) -> Tuple[int, int]:
        """Chọn ô tiếp theo để bắn dựa trên chiến lược tối ưu"""
        # Nếu đang trong chế độ săn tàu
        if self.hunt_stack:
            return self.hunt_stack.pop()
            
        # Cập nhật bản đồ xác suất
        self.update_probability_map()
        
        # Sử dụng chiến lược parity khi chưa có hit
        if not self.hits:
            parity_cells = self._get_parity_cells()
            if parity_cells:
                # Chọn ô có xác suất cao nhất trong các ô parity
                max_prob = 0
                best_cell = parity_cells[0]
                for cell in parity_cells:
                    if self.probability_map[cell[0]][cell[1]] > max_prob:
                        max_prob = self.probability_map[cell[0]][cell[1]]
                        best_cell = cell
                return best_cell
        
        # Chọn ô có xác suất cao nhất
        max_prob = np.max(self.probability_map)
        if max_prob > 0:
            candidates = list(zip(*np.where(self.probability_map == max_prob)))
            return random.choice(candidates)
        
        # Nếu không tìm thấy ô nào, chọn ngẫu nhiên từ các ô còn lại
        empty_cells = [
            (i, j) for i in range(self.board_size)
            for j in range(self.board_size)
            if (i, j) not in self.hits and (i, j) not in self.misses
        ]
        return random.choice(empty_cells) if empty_cells else (0, 0)

    def update_game_state(self, x: int, y: int, is_hit: bool):
        """Cập nhật trạng thái game sau mỗi lượt bắn"""
        if is_hit:
            self.hits.add((x, y))
            
            # Kiểm tra xem có tàu nào bị đánh chìm không
            ship_length = self._find_ship_length(x, y)
            for ship_name, length in list(self.remaining_ships.items()):
                if length == ship_length:
                    del self.remaining_ships[ship_name]
                    # Đánh dấu các ô đã xác nhận có tàu
                    for hit_x, hit_y in self.hits:
                        if self._find_ship_length(hit_x, hit_y) == ship_length:
                            self.confirmed_ship_cells.add((hit_x, hit_y))
                    break
            
            # Thêm các ô xung quanh vào hunt_stack
            adjacent_cells = self._get_adjacent_cells(x, y)
            self.hunt_stack.extend(adjacent_cells)
        else:
            self.misses.add((x, y))
            if (x, y) in self.hunt_stack:
                self.hunt_stack.remove((x, y))
            
            # Đổi hướng tìm kiếm nếu miss
            if self.hunting_direction:
                self.hunting_direction = None
                self.hunt_stack = []

        # Đổi parity nếu không còn ô phù hợp
        if not self._get_parity_cells():
            self.parity = not self.parity

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
        
        # Ghi ra file moves.txt
        with open("moves.txt", "w", encoding="utf-8") as f:
            # In bảng ban đầu
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
                
                if is_hit:
                    game.update_ship_hits(x, y)
                
                self.update_game_state(x, y, is_hit)
                moves.append((x, y, is_hit))
                
                # Ghi thông tin về nước đi
                f.write(f"{move_count:4d}  ({x},{y})    {'Hit' if is_hit else 'Miss'}    ")
                
                # Tạo bảng hiện tại
                current_board = np.full((self.board_size, self.board_size), '-')
                for hit_x, hit_y in self.hits:
                    current_board[hit_x][hit_y] = 'H'
                for miss_x, miss_y in self.misses:
                    current_board[miss_x][miss_y] = 'M'
                
                # In bảng sau mỗi nước đi
                f.write("\n")
                f.write("   " + " ".join(str(i) for i in range(self.board_size)) + "\n")
                for i in range(self.board_size):
                    f.write(f"{i:2}|")
                    for j in range(self.board_size):
                        f.write(current_board[i][j] + " ")
                    f.write("\n")
                f.write("-" * 50 + "\n")
                
                # Kiểm tra xem đã bắn trúng hết tàu chưa
                if all(ship.is_sunk() for ship in game.ships):
                    break
            
            # Thống kê cuối game
            f.write("\nGame Summary:\n")
            f.write(f"Total moves: {move_count}\n")
            f.write(f"Total hits: {len(self.hits)}\n")
            f.write(f"Total misses: {len(self.misses)}\n")
            f.write(f"Hit ratio: {len(self.hits)/move_count:.2%}\n")
            
            # In trạng thái cuối cùng của các tàu
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