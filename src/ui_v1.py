import tkinter as tk
from tkinter import messagebox
import random
from typing import List, Tuple, Optional

from ai_ga import GeneticBattleshipAI
from game import BattleshipGame
from ship import Ship
from ai import BattleshipAI
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

SHIP_PREVIEW_COLOR = "#e0c1e6"
SHIP_PLACED_COLOR = "#c58ad0"
ATTACK_MISSED = "#b0b0b0"
ATTACK_HIT = "#ff5733"
class HomePage:
    def __init__(self, master):
        self.master = master
        self.master.title("Battleship")
        
        # Set window to fullscreen
        self.master.attributes('-fullscreen', True)
        
        # Create main frame
        self.frame = tk.Frame(master)
        self.frame.pack(expand=True)
        
        # Game title
        title_label = tk.Label(self.frame, 
                             text="BATTLESHIP", 
                             font=('Arial', 48, 'bold'))
        title_label.pack(pady=50)
        
        # Authors
        authors_text = "22110052 - Dang Huu Loc\n22110065 - Nguyen Nhat Quang\n22110067 - Nguyen Quang Sang"
        authors_label = tk.Label(self.frame, 
                               text=authors_text,
                               font=('Arial', 14))
        authors_label.pack(pady=30)
        
        # Start button
        start_button = ttk.Button(self.frame,
                                text="Start Game",
                                command=self.show_tutorial,
                                style='Large.TButton',
                                cursor="hand2")
        start_button.pack(pady=40)
        
        # Configure button style
        style = ttk.Style()
        style.theme_use('alt')
        style.configure('Large.TButton', 
                       font=('Arial', 16), 
                       padding=10,
                       background="",
                       foreground="white")
        style.map("Large.TButton", background=[('!active', '#8782BC'), ("pressed", "#A5A1CD"), ("active", "#afaad2")])
        # Exit button
        exit_button = ttk.Button(self.frame,
                               text="Exit",
                               command=self.master.quit, cursor="hand2")
        exit_button.pack(pady=20)

    def show_tutorial(self):
        self.frame.destroy()
        TutorialPage(self.master)

class TutorialPage:
    def __init__(self, master):
        self.master = master
        
        # Create main frame
        self.frame = tk.Frame(master)
        self.frame.pack(expand=True, fill='both')
        
        # Load and display tutorial image
        image = Image.open("tutorial.png")
        # Resize image to fit screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        image = image.resize((screen_width, screen_height - 100))  # Leave space for button
        
        self.photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(self.frame, image=self.photo)
        image_label.pack(expand=True, fill='both')
        
        # Start button
        start_button = ttk.Button(self.frame,
                                text="Start",
                                command=self.start_game,
                                style='Large.TButton', cursor="hand2")
        start_button.pack(pady=20)

    def start_game(self):
        self.frame.destroy()
        BattleshipGUI(self.master)

class BattleshipGUI:
    def __init__(self, master):

        self.restart_img = ImageTk.PhotoImage(Image.open("restart.png").resize((60, 50)))
        
        self.algorithms = tk.StringVar(value="Probability")

        self.master = master
        self.master.title("Battleship Game")
        
        # Initialize variables
        self.setup_new_game()

        # Cấu hình grid trong `master` để game_frame chiếm toàn bộ
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        
        # Create main game frame
        self.game_frame = tk.Frame(master, bg="lightblue")
        self.game_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Cấu hình grid trong `game_frame` thành layout 4x8
        frame_width = self.game_frame.winfo_width()
        frame_height = self.game_frame.winfo_height()
        for i in range(6):
            self.game_frame.grid_rowconfigure(i, weight=1, minsize=frame_height//4)
        for j in range(8):
            self.game_frame.grid_columnconfigure(j, weight=1, minsize=frame_width//8)
        # self.show_grid_layout(self.game_frame, 6, 8)

        # "Your Board" frame
        self.player_frame = tk.LabelFrame(self.game_frame, text="Your Board", padx=10, pady=10, font=('Arial', 15), border=0)
        self.player_frame.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nsew", padx=10, pady=10)

        # "AI's Board" frame
        self.ai_frame = tk.LabelFrame(self.game_frame, text="AI's Board", padx=10, pady=10, font=('Arial', 15), border=0)
        self.ai_frame.grid(row=0, column=3, rowspan=3, columnspan=3, sticky="nsew", padx=10, pady=10)

        # Instructions
        self.instructions_frame = tk.LabelFrame(self.game_frame, text="Instructions", padx=10, pady=10, font=('Arial', 15), border=0, bg="white")
        self.instructions_frame.grid(row=0, column=6, columnspan=2, rowspan=3, sticky="nsew", padx=10, pady=10)

        # "Your Ships" frame
        self.player_ships_frame = tk.LabelFrame(self.game_frame, text="Your Ships", padx=10, pady=5, font=('Arial', 15), border=0)
        self.player_ships_frame.grid(row=3, column=0,columnspan=1, sticky="nsew", padx=10, pady=10)

        # Control frame
        self.control_frame = tk.Frame(self.game_frame, padx=10, pady=10)
        self.control_frame.grid(row=3, column=1, columnspan=4, sticky="nsew", padx=10, pady=10)

        # "AI Ships" frame
        self.ai_ships_frame = tk.LabelFrame(self.game_frame, text="AI Ships", padx=10, pady=5, font=('Arial', 15), border=0)
        self.ai_ships_frame.grid(row=3, column=5, sticky="nsew", padx=10, pady=10)

        # Create status label
        self.status_label = tk.Label(self.control_frame, text="Place your ships!", font=('Arial', 15))
        self.status_label.pack(pady=(10, 20))

        self.show_probability = tk.BooleanVar(value=False)
    
        # Tạo checkbox
        self.prob_checkbox = tk.Checkbutton(
            self.control_frame,
            text="Show AI Probability",
            variable=self.show_probability,
            command=self.toggle_probability_display
        )
        
        # Create algorithm frame
        self.algorithm_frame = tk.LabelFrame(self.game_frame, text="Algorithm", padx=10, pady=5, font=('Arial', 15), border=0, bg='white')
        self.algorithm_frame.grid(row=3, column=6, sticky='nsew', padx=10, pady=10)
        
        # Tạo radio buttons
        self.algorithms.set("Probability")
        self.algorithm_prob = ttk.Radiobutton(self.algorithm_frame,
                                        text='Probability',
                                        value='Probability',
                                        variable=self.algorithms,
                                        style='TRadiobutton',
                                        command=self.restart_game)
        self.algorithm_prob.pack(pady=5)
        self.algorithm_genetic = ttk.Radiobutton(self.algorithm_frame,
                                        text='Genetic Algorithm',
                                        value='Genetic',
                                        variable=self.algorithms,
                                        style='TRadiobutton',
                                        command=self.restart_game)
        self.algorithm_genetic.pack(pady=5)

        self.radio_style = ttk.Style()
        self.radio_style.theme_use("alt")
        self.radio_style.configure('TRadiobutton', cursor="hand2", bg="white")
        self.radio_style.map("TRadiobutton", background=[('!active', 'white'), ("pressed", "gray"), ("active", "lightgray")])

        # Create ship status frames
        self.create_ship_status_frames()

        # Create board frames
        self.create_board_frames()

        # Create control buttons
        self.create_control_buttons()

        # Start ship placement phase
        self.start_ship_placement()

    def show_grid_layout(self, frame, rows, columns):
        for r in range(rows):
            for c in range(columns):
                # Tạo ô giả lập
                tk.Label(
                    frame,
                    text=f"R{r}\nC{c}",
                    borderwidth=1,
                    relief="solid",
                    bg="lightgray"
                ).grid(row=r, column=c, sticky="nsew")

    def setup_new_game(self):
        """Initialize all game variables for a new game"""
        self.player_game = BattleshipGame()
        print("ALGORITHM:", self.algorithms.get())
        if self.algorithms.get() == "Probability":
            print("Using prob")
            self.ai = BattleshipAI()
        elif self.algorithms.get() == "Genetic":
            print("Using genetic")
            self.ai = GeneticBattleshipAI()
            self.ai.load_strategy("4.json")
        self.ai_game = BattleshipGame()
        
        # Clear existing ship positions
        self.player_game.board = self.player_game.board = [[' ' for _ in range(10)] for _ in range(10)]
        self.player_game.ships = []
        
        # Game state variables
        self.is_player_turn = True
        self.game_over = False
        self.setup_phase = True
        
        # Ship placement variables
        self.ships_to_place = [
            ("Carrier", 5),
            ("Battleship", 4),
            ("Cruiser", 3),
            ("Submarine", 3),
            ("Destroyer", 2)
        ]
        self.current_ship_index = 0
        self.is_horizontal = True
        self.placement_preview = set()  # Store cells being previewed
    
    def create_board_frames(self):
        # Create board buttons
        self.player_buttons = []
        self.ai_buttons = []
        
        for i in range(10):
            player_row = []
            ai_row = []
            for j in range(10):
                # Player's board buttons - increased width for probability numbers
                p_btn = tk.Button(self.player_frame, width=8, height=3, cursor='hand2')
                p_btn.grid(row=i+1, column=j+1)
                p_btn.bind('<Enter>', lambda e, x=i, y=j: self.preview_ship_placement(x, y))
                p_btn.bind('<Leave>', lambda e: self.clear_ship_preview())
                p_btn.bind('<Button-1>', lambda e, x=i, y=j: self.place_ship(x, y))
                p_btn.bind('<Button-3>', lambda e, x=i, y=j: self.toggle_ship_orientation(x, y))
                player_row.append(p_btn)
                
                # AI's board buttons
                ai_btn = tk.Button(self.ai_frame, width=8, height=3)
                ai_btn.grid(row=i+1, column=j+1)
                ai_btn.configure(state='disabled')  # Disabled during setup
                ai_row.append(ai_btn)
            
            self.player_buttons.append(player_row)
            self.ai_buttons.append(ai_row)
        # Make grid cells expand with the window size
        for i in range(10):
            self.player_frame.grid_rowconfigure(i + 1, weight=1)
            self.player_frame.grid_columnconfigure(i + 1, weight=1)
            self.ai_frame.grid_rowconfigure(i + 1, weight=1)
            self.ai_frame.grid_columnconfigure(i + 1, weight=1)
        # Add row/column labels
        for i in range(10):
            # Row labels
            tk.Label(self.player_frame, text=str(i)).grid(row=i+1, column=0)
            tk.Label(self.ai_frame, text=str(i)).grid(row=i+1, column=0)
            
            # Column labels
            tk.Label(self.player_frame, text=str(i)).grid(row=0, column=i+1)
            tk.Label(self.ai_frame, text=str(i)).grid(row=0, column=i+1)
    def resize_buttons(self, event):
        # Calculate new dimensions based on window size
        new_width = max(5, event.width // 20) 
        new_height = max(2, event.height // 40)

        # Update all player buttons
        for row in self.player_buttons:
            for button in row:
                button.config(width=new_width, height=new_height)

        # Update all AI buttons
        for row in self.ai_buttons:
            for button in row:
                button.config(width=new_width, height=new_height)
                
    def create_ship_status_frames(self): 
        # Add ship status labels
        self.player_ship_labels = {}
        self.ai_ship_labels = {}
        
        for ship_name, length in self.ships_to_place:
            label = tk.Label(self.player_ships_frame, 
                           text=f"{ship_name} ({length}): Not Placed", 
                           fg="orange")
            label.pack(anchor="w")
            self.player_ship_labels[ship_name] = label

        # Initialize AI ships display
        for ship in self.ai_game.ships:
            label = tk.Label(self.ai_ships_frame, 
                           text=f"{ship.name} ({ship.length}): Waiting", 
                           fg="red")
            label.pack(anchor="w")
            self.ai_ship_labels[ship.name] = label
    
    def create_control_buttons(self):
        # Create a new frame for buttons
        self.buttons_frame = tk.Frame(self.control_frame)
        self.buttons_frame.pack()
        
        # Create restart button (initially disabled)
        self.restart_button = tk.Button(self.buttons_frame,
                                    image=self.restart_img, 
                                    command=self.restart_game,
                                    state='disabled')
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        # Create reset placement button
        self.reset_placement_button = tk.Button(self.buttons_frame,
                                            text="Reset Placement", 
                                            command=self.reset_placement)
        self.reset_placement_button.pack(side=tk.LEFT, padx=5)
        
        self.instruction_image = Image.open("side tutorial.png")
        self.instruction_photo = ImageTk.PhotoImage(self.instruction_image)
        # Create instructions label
        self.instructions_label = tk.Label(
            self.instructions_frame, 
            image=self.instruction_photo,
        )
        self.instructions_label.pack()
    
    def start_ship_placement(self):
        """Start the ship placement phase"""
        self.setup_phase = True
        self.current_ship_index = 0
        self.is_horizontal = True
        self.update_placement_status()
        
        # Enable player board, disable AI board
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j]['state'] = 'normal'
                self.ai_buttons[i][j]['state'] = 'disabled'
    
    def toggle_ship_orientation(self, x: int, y: int):
        """Toggle ship orientation between horizontal and vertical"""
        self.is_horizontal = not self.is_horizontal
        self.status_label.configure(
            text=f"Placing {self.ships_to_place[self.current_ship_index][0]} "
                 f"({'Horizontal' if self.is_horizontal else 'Vertical'})"
        )
        self.clear_ship_preview()
        self.preview_ship_placement(x, y)
    
    def preview_ship_placement(self, x: int, y: int):
        """Preview ship placement when hovering over cells"""
        if not self.setup_phase or self.current_ship_index >= len(self.ships_to_place):
            return
        
        self.clear_ship_preview()
        ship_name, ship_length = self.ships_to_place[self.current_ship_index]
        
        # Calculate ship positions
        positions = self.get_ship_positions(x, y, ship_length)
        if not positions:  # Invalid placement
            return
        
        # Show preview
        self.placement_preview = set(positions)
        for px, py in positions:
            self.player_buttons[px][py].configure(bg=SHIP_PREVIEW_COLOR)
    
    def clear_ship_preview(self):
        """Clear the ship placement preview"""
        for x, y in self.placement_preview:
            if self.player_game.board[x][y] == ' ':
                self.player_buttons[x][y].configure(bg="SystemButtonFace")
        self.placement_preview.clear()
    
    def get_ship_positions(self, x: int, y: int, length: int) -> List[Tuple[int, int]]:
        """Get list of positions for ship placement, or empty list if invalid"""
        positions = []
        if self.is_horizontal:
            if y + length > 10:  # Out of bounds
                return []
            positions = [(x, y + i) for i in range(length)]
        else:
            if x + length > 10:  # Out of bounds
                return []
            positions = [(x + i, y) for i in range(length)]
        
        # Check for overlapping ships
        for px, py in positions:
            if self.player_game.board[px][py] != ' ':
                return []
            
            # # Check adjacent cells
            # for dx in [-1, 0, 1]:
            #     for dy in [-1, 0, 1]:
            #         nx, ny = px + dx, py + dy
            #         if (0 <= nx < 10 and 0 <= ny < 10 and 
            #                 self.player_game.board[nx][ny] != ' ' and 
            #                 (nx, ny) not in positions):
            #             return []
        
        return positions
    
    def place_ship(self, x: int, y: int):
        """Place a ship at the specified position"""
        if not self.setup_phase or self.current_ship_index >= len(self.ships_to_place):
            return
        
        ship_name, ship_length = self.ships_to_place[self.current_ship_index]
        positions = self.get_ship_positions(x, y, ship_length)
        
        if not positions:
            return
        
        # Place the ship
        ship = Ship(ship_name, ship_length)
        ship.positions = positions
        self.player_game.ships.append(ship)
        
        for px, py in positions:
            self.player_game.board[px][py] = ship_name[0]
            self.player_buttons[px][py].configure(bg=SHIP_PLACED_COLOR)
        
        # Update ship status
        self.player_ship_labels[ship_name].configure(
            text=f"{ship_name} ({ship_length}): Active",
            fg="green"
        )
        
        # Move to next ship
        self.current_ship_index += 1
        if self.current_ship_index >= len(self.ships_to_place):
            self.finish_setup()
        else:
            self.update_placement_status()
    
    def update_placement_status(self):
        """Update status label during ship placement"""
        if self.current_ship_index < len(self.ships_to_place):
            ship_name = self.ships_to_place[self.current_ship_index][0]
            self.status_label.configure(
                text=f"Place your {ship_name} "
                     f"({'Horizontal' if self.is_horizontal else 'Vertical'})\n"
                     "Right-click to rotate"
            )
    
    def handle_ai_board_btn_enter(self, x, y):
        bg = self.ai_buttons[x][y].cget('bg')
        if bg == 'SystemButtonFace':
            self.ai_buttons[x][y].configure(bg='gray')

    def handle_ai_board_btn_leave(self, x, y):
        # Check if this position was hit on any ship
        is_hit = False
        for ship in self.ai_game.ships:
            if (x, y) in ship.hits:
                self.ai_buttons[x][y].configure(bg=ATTACK_HIT)
                is_hit = True
                break
        
        # If it's not a hit but the background isn't default, it must be a miss
        if not is_hit:
            bg = self.ai_buttons[x][y].cget('bg')
            if bg != 'SystemButtonFace' and bg != 'gray':
                self.ai_buttons[x][y].configure(bg=ATTACK_MISSED)
            else:
                self.ai_buttons[x][y].configure(bg='SystemButtonFace')
                    
    def finish_setup(self):
        """Finish the setup phase and start the game"""
        self.setup_phase = False
        self.is_player_turn = True
        # Enable AI board for attacks
        for i in range(10):
            for j in range(10):
                self.ai_buttons[i][j].configure(state='normal')
                self.ai_buttons[i][j].configure(
                    command=lambda x=i, y=j: self.handle_player_move(x, y)
                )
                self.ai_buttons[i][j].configure(cursor="cross")
                self.ai_buttons[i][j].bind('<Enter>', lambda e, x=i, y=j: self.handle_ai_board_btn_enter(x, y))
                self.ai_buttons[i][j].bind('<Leave>', lambda e, x=i, y=j: self.handle_ai_board_btn_leave(x, y))
        for widget in self.ai_ships_frame.winfo_children():
            widget.destroy()        
        # Initialize AI ships display
        for ship in self.ai_game.ships:
            label = tk.Label(self.ai_ships_frame, 
                           text=f"{ship.name} ({ship.length}): Active", 
                           fg="green")
            label.pack(anchor="w")
            self.ai_ship_labels[ship.name] = label
        
        # Update status
        self.status_label.configure(text="Your turn! Click on AI's board to attack")
        self.reset_placement_button.configure(state='disabled')
        # Enable restart button when game starts
        self.restart_button.configure(state='normal')
        self.prob_checkbox.pack(pady=10)
    
    def reset_placement(self):
        """Reset the ship placement phase"""
        # Clear board
        self.player_game.board = [[' ' for _ in range(10)] for _ in range(10)]
        self.player_game.ships = []
        
        # Reset buttons
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j].configure(bg="SystemButtonFace")
        
        # Reset ship labels
        for ship_name, length in self.ships_to_place:
            self.player_ship_labels[ship_name].configure(
                text=f"{ship_name} ({length}): Not Placed",
                fg="orange"
            )
        
        # Restart placement
        self.current_ship_index = 0
        self.update_placement_status()
    
    def restart_game(self):
        """Restart the entire game"""
        # If game is in progress (not over), show confirmation dialog
        if not self.game_over and not self.setup_phase:
            if not messagebox.askyesno("Confirm Restart", "Are you sure you want to restart the game?"):
                return        
        # Reset AI ships frame
        for widget in self.ai_ships_frame.winfo_children():
            widget.destroy()
        for ship in self.ai_game.ships:
            label = tk.Label(self.ai_ships_frame, 
                           text=f"{ship.name} ({ship.length}): Waiting", 
                           fg="red")
            label.pack(anchor="w")
            self.ai_ship_labels[ship.name] = label
        
        # Reset game state
        self.setup_new_game()
        
        # Reset all buttons
        for i in range(10):
            for j in range(10):
                self.player_buttons[i][j].configure(
                    bg="SystemButtonFace",
                    state='normal'
                )
                self.ai_buttons[i][j].configure(
                    bg="SystemButtonFace",
                    state='disabled'
                )
        
        # Reset ship labels
        for ship_name, length in self.ships_to_place:
            self.player_ship_labels[ship_name].configure(
                text=f"{ship_name} ({length}): Not Placed",
                fg="orange"
            )
        
        # Enable reset placement button
        self.reset_placement_button.configure(state='normal')
        
        # Disable restart button
        self.restart_button.configure(state='disabled')
        self.show_probability.set(False)
        self.prob_checkbox.pack_forget()
        # Start placement phase
        self.start_ship_placement()
    
    def handle_player_move(self, x: int, y: int):
        if not self.is_player_turn or self.game_over:
            return
        
        # Check if cell was already hit
        if self.ai_buttons[x][y]['state'] == 'disabled':
            return
        
        # Process player's move
        is_hit = self.ai_game.check_hit(x, y)
        self.ai_buttons[x][y]['state'] = 'disabled'
        
        if is_hit:
            self.ai_buttons[x][y].configure(bg=ATTACK_HIT)
            # Find hit ship and update status
            for ship in self.ai_game.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    if ship.is_sunk():
                        self.ai_ship_labels[ship.name].configure(
                            text=f"{ship.name} ({ship.length}): Sunk", 
                            fg="red"
                        )
        else:
            self.ai_buttons[x][y].configure(bg=ATTACK_MISSED)
        
        # Check for game over
        if all(ship.is_sunk() for ship in self.ai_game.ships):
            self.game_over = True
            messagebox.showinfo("Game Over", "Congratulations! You won!")
            return
        
        # Switch turns
        self.is_player_turn = False
        self.status_label.configure(text="AI's turn...")
        
        if self.algorithms.get() == "Probability":
            # Update probability heatmap before AI's move
            self.update_probability_heatmap()
            self.master.after(1000, self.handle_ai_move)
        elif self.algorithms.get() == "Genetic":
            self.master.after(1000, self.handle_ga_move)
    
    def toggle_probability_display(self):
        """Toggle probability display on/off"""
        if self.show_probability.get():
            self.update_probability_heatmap()
        else:
            # Clear all probability numbers
            for i in range(10):
                for j in range(10):
                    if self.player_buttons[i][j]['bg'] not in [ATTACK_HIT, ATTACK_MISSED]:
                        self.player_buttons[i][j].configure(text="")

    def update_probability_heatmap(self):
        """Update the player's board visualization with AI's probability numbers"""
        # Nếu checkbox không được chọn, không hiển thị số
        if not self.show_probability.get():
            return

        print(self.ai.probability_map)
        print("=======================")
        for i in range(10):
            for j in range(10):
                # Skip cells that have been hit
                if self.player_buttons[i][j]['bg'] in [ATTACK_HIT, ATTACK_MISSED]:
                    continue
                    
                # Get probability and format it
                prob = self.ai.probability_map[i][j]
                if prob == 0:
                    text = "-"  # Empty text for zero probability 
                else:
                    # Format to 2 decimal places
                    if prob < 100:
                        text = f"{prob * 100:.2f}"
                    else:
                        text = f"{prob:.2f}"
                
                # Update button text
                self.player_buttons[i][j].configure(text=text)

    def handle_ga_move(self):
        if self.game_over:
            return
        x, y = self.ai.get_next_target(self.ai.best_strategy)
        is_hit = self.player_game.check_hit(x, y)
        
        if is_hit:
            self.ai.hits.add((x, y))
            self.ai.unconfirmed_hits.add((x, y))
            hit_ship = None
            for ship in self.player_game.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    hit_ship = ship
                    if ship.is_sunk():
                        self.player_ship_labels[ship.name].configure(
                            text=f"{ship.name} ({ship.length}): Sunk", 
                            fg="red"
                        )
                        self.ai.sunk_ship_positions.update(hit_ship.positions)
                        self.ai.unconfirmed_hits -= set(hit_ship.positions)
                        for ship_name, length in list(self.ai.remaining_ships.items()):
                            if length == len(hit_ship.positions):
                                del self.ai.remaining_ships[ship_name]
                                break
        else:
            self.ai.misses.add((x, y))
        print(x, y, is_hit)
        # Update visual representation
        self.player_buttons[x][y].configure(
            bg=ATTACK_HIT if is_hit else ATTACK_MISSED
        )
        
        # Check for game over
        if all(ship.is_sunk() for ship in self.player_game.ships):
            self.game_over = True
            messagebox.showinfo("Game Over", "AI won! Better luck next time!")
            return
        
        # Switch turns
        self.is_player_turn = True
        self.status_label.configure(text="Your turn! Click on AI's board to attack")
        # moves.append((x, y, is_hit))
        
    def handle_ai_move(self):
        if self.game_over:
            return
        
        # Get AI's move
        x, y = self.ai.get_next_target()
        is_hit = self.player_game.check_hit(x, y)
        
        # Find hit ship if it's a hit
        hit_ship = None
        if is_hit:
            for ship in self.player_game.ships:
                if (x, y) in ship.positions:
                    ship.hits.add((x, y))
                    hit_ship = ship
                    if ship.is_sunk():
                        self.player_ship_labels[ship.name].configure(
                            text=f"{ship.name} ({ship.length}): Sunk", 
                            fg="red"
                        )
                    break
        
        # Update AI's game state
        self.ai.update_game_state(x, y, is_hit, hit_ship)
        
        # Update visual representation
        self.player_buttons[x][y].configure(
            bg=ATTACK_HIT if is_hit else ATTACK_MISSED
        )
        
        # Check for game over
        if all(ship.is_sunk() for ship in self.player_game.ships):
            self.game_over = True
            messagebox.showinfo("Game Over", "AI won! Better luck next time!")
            return
        
        # Switch turns
        self.is_player_turn = True
        self.status_label.configure(text="Your turn! Click on AI's board to attack")
    
# Modify the main function
def main():
    root = tk.Tk()
    HomePage(root)
    root.mainloop()

if __name__ == "__main__":
    main()