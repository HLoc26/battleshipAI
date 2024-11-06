import numpy as np
from typing import List, Tuple, Set, Dict, Optional
import random

from game import BattleshipGame
from ship import Ship, Direction

class BattleshipAI:
    def __init__(self, board_size: int = 10):
        self.board_size = board_size # Kích thước bàn cờ 
        self.probability_map = np.ones((board_size, board_size)) # Bảng xác suất 
        self.hits = set() # Tập hợp các ô đã đánh trúng
        self.misses = set() # Tập hợp các ô đánh hụt
        self.ships = { # Danh sách các tàu (tên tàu và kích thước)
            'Carrier': 5,
            'Battleship': 4,
            'Cruiser': 3,
            'Submarine': 3,
            'Destroyer': 2
        }
        self.remaining_ships = self.ships.copy() # Danh sách các tàu còn lại (vì mới khởi tạo nên copy của ships)
        self.hunt_stack = []
        self.last_hits = []
        self.confirmed_ship_cells = set()
        self.unconfirmed_hits = set() # Tập hợp những ô đã hit nhưng chưa chìm tàu
        self.sunk_ship_positions = set()
        self.min_remaining_ship_size = min(self.ships.values())
        self.max_remaining_ship_size = max(self.ships.values()) 

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
                        self.hunt_stack.insert(0, (new_x, new_y))
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
    
    def can_fit_smallest_ship(self, x: int, y: int) -> bool:
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

    def calculate_ship_probability(self, ship_length: int) -> np.ndarray:
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

        # Reset lại bảng xác suất
        self.probability_map = np.zeros((self.board_size, self.board_size))
        
        # Chỉ tính xác suất cho các tàu còn lại
        for _, ship_length in self.remaining_ships.items():
            ship_probability = self.calculate_ship_probability(ship_length)
            self.probability_map += ship_probability
        
        # Áp dụng các ràng buộc bổ sung
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i, j) in self.hits or (i, j) in self.misses:
                    self.probability_map[i][j] = 0
                elif not self.can_fit_smallest_ship(i, j):
                    self.probability_map[i][j] = 0
        
        # Normalize probability map
        total = np.sum(self.probability_map)
        if total > 0:
            self.probability_map /= total


    def is_late_game(self) -> bool:
        """Kiểm tra xem có phải là cuối game rồi hay không (số tàu còn lại dưới 3)
        
        Trả về
        -------
        bool
            True nếu là cuối game (số tàu còn lại dưới 3)
            False nếu chưa cuối game (số tàu còn lại >= 3)"""
        return len(self.remaining_ships) <= 2

    def calculate_ship_density(self, x: int, y: int) -> float:
        """Kiểm tra xem có bao nhiêu cách đặt tàu lên một ô
        
        Tham số
        -------
        x: `int`

            Toạ độ `x` cần kiểm tra (toạ độ hàng)

        y: `int`

            Toạ độ `y` cần kiểm tra (toạ độ cột)

        Trả về
        ------
        density: float

            Số lượng tàu có thể đặt lên ô `(x, y)`

        """
        density = 0 # Khởi tạo density = 0
        # Kiểm tra từng tàu còn lại (self.remaining_ships), lấy ra độ dài của tàu (.values())
        for ship_length in self.remaining_ships.values():
            # Kiểm tra theo chiều ngang
            for start_y in range(max(0, y - ship_length + 1), min(y + 1, self.board_size - ship_length + 1)):
                # Lấy các ô mà tàu đặt lên bắt đầu tại vị trí x, start_y (tăng dần y) 
                positions = [(x, start_y + i) for i in range(ship_length)]
                # Nếu vị trí hợp lệ thì tăng density lên
                if self.is_valid_ship_placement(positions):
                    density += 1

            # Kiểm tra theo chiều dọc
            for start_x in range(max(0, x - ship_length + 1), min(x + 1, self.board_size - ship_length + 1)):
                # Lấy các ô mà tàu đặt lên bắt đầu tại vị trí start_x, y (tăng dần x) 
                positions = [(start_x + i, y) for i in range(ship_length)]
                if self.is_valid_ship_placement(positions):
                    density += 1
                    
        return density

    def is_valid_ship_placement(self, positions: List[Tuple[int, int]]) -> bool:
        """
        Kiểm tra xem vị trí đặt có hợp lệ không
        
        Tham số
        -------
        positions: `List[Tuple[int, int]]`

            Danh sách các tuple, các tuple này có 2 giá trị int, giá trị đầu tiên là vị trí x, giá trị thứ hai là vị trí y
        Trả về
        ------
        bool
            True nếu tất cả các ô mà tàu đặt lên (`positions`) đều hợp lệ

            False nếu có một ô nào đó trong `positions` không hợp lệ

        Hợp lệ: 
            Không nằm ngoài bàn cờ
            
            Không nằm trên các ô đã miss hoặc tàu chìm

            Không nằm gần tàu chìm

            Nếu số lượng các ô bị "hit" nhưng chưa chìm trong positions 
            bằng với tổng số ô của positions có mặt trong unconfirmed_hits
        """
        # Kiểm tra với từng toạ độ x, y trong positions
        for x, y in positions:
            # Kiểm tra x và y có nằm trong bàn cờ không (0 <= x, y <= board_size)
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
            
            # Kiểm tra xem (x, y) có nằm trong các ô đã missed hoặc các ô có tàu bị chìm không
            if (x, y) in self.misses or (x, y) in self.sunk_ship_positions:
                return False
            
            # Kiểm tra xem (x, y) có nằm gần tàu bị chìm hay không
            # for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            #     adj_x, adj_y = x + dx, y + dy
            #     if (adj_x, adj_y) in self.sunk_ship_positions:
            #         return False

        # Đếm số lượng các ô đã hit nhưng chưa chìm
        hits_in_placement = sum(1 for pos in positions if pos in self.unconfirmed_hits)
        # Nếu số lượng các ô bị "hit" nhưng chưa chìm trong positions 
        # bằng với tổng số ô của positions có mặt trong unconfirmed_hits
        return hits_in_placement == len(set(positions) & self.unconfirmed_hits)

    def update_late_game_probabilities(self):
        """Cập nhật lại bảng xác suất trong trường hợp late game (còn dưới 3 tàu)"""
        # Reset lại bảng xác suất
        self.probability_map = np.zeros((self.board_size, self.board_size))
        
        # Dùng hàm calculate_ship_density để tính xác suất ban đầu của từng ô
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Nếu ô hiện tại (i, j) không phải ô đã đánh
                if (i, j) not in self.hits and (i, j) not in self.misses:
                    self.probability_map[i, j] = self.calculate_ship_density(i, j)

        # Điều chỉnh tỉ lệ dựa vào unconfirmed_hits (những ô đã hit nhưng chưa chìm)
        if self.unconfirmed_hits: # Nếu có những ô như vậy
            # Duyệt qua từng ô và cập nhật lại
            for hit_x, hit_y in self.unconfirmed_hits:
                # Tăng tỉ lệ các ô thẳng hàng với các ô không chắc chắn
                for ship_length in self.remaining_ships.values():
                    # Tăng theo hàng ngang
                    for y in range(max(0, hit_y - ship_length + 1), min(hit_y + ship_length, self.board_size)):
                        if (hit_x, y) not in self.hits and (hit_x, y) not in self.misses:
                            self.probability_map[hit_x, y] *= 2

                    # Tăng theo hàng dọc
                    for x in range(max(0, hit_x - ship_length + 1), min(hit_x + ship_length, self.board_size)):
                        if (x, hit_y) not in self.hits and (x, hit_y) not in self.misses:
                            self.probability_map[x, hit_y] *= 2

        # Tìm những ô không thể đặt tàu
        invalid_positions = set() # Tập hợp các vị trí không phù hợp
        # Kiểm tra từng ô
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Nếu ô đó chưa đánh
                if (i, j) not in self.hits and (i, j) not in self.misses:
                    # Kiểm tra xem ô đó có thể đặt tàu hay không
                    can_fit_ship = False
                    # Kiểm tra với mỗi tàu còn lại, có thể đặt tàu vào hay không
                    for ship_length in self.remaining_ships.values():
                        # Kiểm tra theo hàng ngang (đếm số lượng ô trống hai bên ô (i, j))
                        horizontal_space = self.get_available_space(i, j, True)
                        # Kiểm tra theo hàng dọc (đếm số lượng ô trống trên dưới ô (i, j))
                        vertical_space = self.get_available_space(i, j, False)
                        # Nếu số lượng ô trống đủ để đặt tàu thì báo là ô (i, j) có thể đặt ít nhất một tàu
                        if horizontal_space >= ship_length or vertical_space >= ship_length:
                            can_fit_ship = True
                            break
                    # Nếu không thể đặt tàu thì thêm ô đó vào invalid positions
                    if not can_fit_ship:
                        invalid_positions.add((i, j))
                        # Và cập nhật lại bảng xác suất, cho ô đó = 0 (không thể xếp tàu lên ô này)
                        self.probability_map[i, j] = 0

    def get_available_space(self, x: int, y: int, horizontal: bool) -> int:
        """Đếm số lượng ô trống xung quanh (trên/dưới và trái/phải) một ô có toạ độ `(x, y)`
        
        Tham số
        -------
        x: int

            Toạ độ x cần kiểm tra

        y: int

            Toạ độ y cần kiểm tra

        horizontal: bool

            Báo cho hàm biết là cần kiểm tra theo chiều dọc hay chiều ngang
        Trả về
        ------
        int: Số lượng ô trống xung quanh ô (x, y)
        """
        space = 0 # Đếm số ô trống
        if horizontal: # Đếm theo chiều ngang
            # Bắt đầu từ ô hiện tại đến ô ngoài cùng bên phải
            for dy in range(self.board_size - y):
                if (x, y + dy) in self.misses or (x, y + dy) in self.sunk_ship_positions:
                    break
                space += 1
        else: # Đếm theo chiều dọc
            for dx in range(self.board_size - x):
                if (x + dx, y) in self.misses or (x + dx, y) in self.sunk_ship_positions:
                    break
                space += 1
        return space
    
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
    batchNum = 100
    runBatch(batchNum)