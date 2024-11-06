import tkinter as tk
from ai import BattleshipAI
from game import BattleshipGame
from tkinter import messagebox

class BattleshipGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Battleship AI vs AI")
        
        # Game objects
        self.setup_new_game()
        
        # GUI elements
        self.setup_gui()
        
        # Start game
        self.start_game()
    
    def setup_new_game(self):
        """Initialize new game objects"""
        self.game1 = BattleshipGame()
        self.game2 = BattleshipGame()
        self.ai1 = BattleshipAI()
        self.ai2 = BattleshipAI()
        
        # Place ships
        self.game1.place_ships()
        self.game2.place_ships()
        
        # Game state
        self.is_game_over = False
        self.is_ai1_turn = True
        self.move_delay = 500  # milliseconds
        
    def setup_gui(self):
        """Setup all GUI elements"""
        # Main frame
        self.main_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_frame.pack()
        
        # Board frames
        self.board1_frame = self.create_board_frame("AI 1's Board", 0)
        self.board2_frame = self.create_board_frame("AI 2's Board", 1)
        
        # Control panel
        self.setup_control_panel()
        
        # Status label
        self.status_label = tk.Label(self.master, text="Game ready!", 
                                   font=('Arial', 12))
        self.status_label.pack(pady=10)
    
    def create_board_frame(self, title: str, col: int) -> tk.Frame:
        """Create a board frame with grid of buttons"""
        frame = tk.LabelFrame(self.main_frame, text=title, padx=10, pady=10)
        frame.grid(row=0, column=col, padx=20)
        
        # Create buttons
        buttons = []
        for i in range(10):
            button_row = []
            for j in range(10):
                btn = tk.Button(frame, width=2, height=1)
                btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                button_row.append(btn)
            buttons.append(button_row)
            
        # Add row/column labels
        for i in range(10):
            tk.Label(frame, text=str(i)).grid(row=0, column=i+1)
            tk.Label(frame, text=str(i)).grid(row=i+1, column=0)
        
        if col == 0:
            self.board1_buttons = buttons
        else:
            self.board2_buttons = buttons
        
        return frame
    
    def setup_control_panel(self):
        """Setup control buttons"""
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=10)
        
        # New Game button
        tk.Button(control_frame, text="New Game", 
                 command=self.new_game).pack(side=tk.LEFT, padx=5)
        
        # Speed control buttons
        tk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=5)
        speeds = [("Fast", 200), ("Normal", 500), ("Slow", 1000)]
        for name, speed in speeds:
            tk.Button(control_frame, text=name,
                     command=lambda s=speed: self.set_speed(s)
                     ).pack(side=tk.LEFT, padx=2)
    
    def set_speed(self, delay: int):
        """Set game speed"""
        self.move_delay = delay
    
    def new_game(self):
        """Start a new game"""
        self.setup_new_game()
        self.clear_boards()
        self.start_game()
    
    def clear_boards(self):
        """Clear both game boards"""
        for buttons in [self.board1_buttons, self.board2_buttons]:
            for row in buttons:
                for button in row:
                    button.configure(bg="SystemButtonFace")
    
    def start_game(self):
        """Start the game"""
        self.is_game_over = False
        self.status_label.configure(text="Game started - AI 1's turn")
        self.master.after(self.move_delay, self.execute_turn)
    
    def execute_turn(self):
        """Execute one turn of the game"""
        if self.is_game_over:
            return
            
        if self.is_ai1_turn:
            attacker = self.ai1
            defender = self.game2
            buttons = self.board2_buttons
            attacker_name = "AI 1"
            defender_name = "AI 2"
        else:
            attacker = self.ai2
            defender = self.game1
            buttons = self.board1_buttons
            attacker_name = "AI 2"
            defender_name = "AI 1"
        
        # Get shot
        x, y = attacker.get_next_target()
        hit, ship = defender.fire(x, y)
        
        # Update display
        buttons[x][y].configure(bg="red" if hit else "blue")
        
        # Update AI
        attacker.update_game_state(x, y, hit, ship)
        
        # Check for game over
        if any(ship.is_sunk() for ship in defender.ships):
            if all(ship.is_sunk() for ship in defender.ships):
                self.is_game_over = True
                self.status_label.configure(text=f"Game Over - {attacker_name} wins!")
                messagebox.showinfo("Game Over", f"{attacker_name} wins!")
                return
        
        # Switch turns
        self.is_ai1_turn = not self.is_ai1_turn
        next_player = "AI 1" if self.is_ai1_turn else "AI 2"
        self.status_label.configure(text=f"{next_player}'s turn")
        
        # Schedule next turn
        self.master.after(self.move_delay, self.execute_turn)

def main():
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()