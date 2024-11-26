import numpy as np
from typing import List, Tuple, Dict
import random
import json
import os
from datetime import datetime
from game import BattleshipGame

class GeneticBattleshipAI:
    def __init__(self, population_size: int = 50, generations: int = 100, board_size: int = 10):
        self.board_size = board_size
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.elite_size = 5
        
        # Initial ships configuration
        self.ships = {
            'Carrier': 5,
            'Battleship': 4,
            'Cruiser': 3,
            'Submarine': 3,
            'Destroyer': 2
        }
        
        # Strategy parameters that will be evolved
        self.strategy_params = {
            'hit_weight': 2.0,  # Weight for targeting cells adjacent to hits
            'pattern_weight': 1.5,  # Weight for checkerboard pattern
            'density_weight': 1.2,  # Weight for ship density calculations
            'edge_weight': 0.8,  # Weight for edge preference
            'exploration_rate': 0.15  # Probability of random exploration
        }
        
        self.population = self._initialize_population()
        self.best_strategy = None
        self.best_fitness = 0.0
        self.hits = set()
        self.misses = set()
        self.remaining_ships = self.ships.copy()
        self.unconfirmed_hits = set()
        self.sunk_ship_positions = set()
        
        # Create strategies directory if it doesn't exist
        os.makedirs('strategies', exist_ok=True)

    def save_strategy(self, filename: str = None) -> str:
        """Save the best evolved strategy to a file
        
        Parameters
        ----------
        filename : str, optional
            Custom filename to save the strategy. If None, generates automated filename.
            
        Returns
        -------
        str
            The filename where the strategy was saved
        """
        if self.best_strategy is None:
            raise ValueError("No strategy to save. Must evolve strategy first using evolve()")
            
        if filename is None:
            # Generate filename with timestamp and fitness score
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategies/strategy_{timestamp}_fitness_{self.best_fitness:.2f}.json"
        else:
            if not filename.endswith('.json'):
                filename = f"strategies/{filename}.json"
            else:
                filename = f"strategies/{filename}"

        # Prepare strategy data with metadata
        strategy_data = {
            'parameters': self.best_strategy,
            'fitness': self.best_fitness,
            'timestamp': datetime.now().isoformat(),
            'generations': self.generations,
            'population_size': self.population_size,
            'board_size': self.board_size
        }
        
        with open(filename, 'w') as f:
            json.dump(strategy_data, f, indent=4)
            
        print(f"Strategy saved to {filename}")
        return filename

    def load_strategy(self, filename: str) -> Dict:
        """Load a previously saved strategy
        
        Parameters
        ----------
        filename : str
            Name of the file to load the strategy from
            
        Returns
        -------
        Dict
            The loaded strategy parameters
        """
        if not filename.endswith('.json'):
            filename = f"strategies/{filename}.json"
        else:
            filename = f"strategies/{filename}"
            
        try:
            with open(filename, 'r') as f:
                strategy_data = json.load(f)
            
            self.best_strategy = strategy_data['parameters']
            self.best_fitness = strategy_data['fitness']
            
            print(f"Loaded strategy from {filename}")
            print(f"Strategy fitness: {self.best_fitness:.2f}")
            print("Strategy parameters:")
            for param, value in self.best_strategy.items():
                print(f"  {param}: {value:.3f}")
                
            return self.best_strategy
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Strategy file {filename} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid strategy file format in {filename}")

    def list_saved_strategies(self) -> List[Dict]:
        """List all saved strategies with their metadata
        
        Returns
        -------
        List[Dict]
            List of dictionaries containing strategy metadata
        """
        strategies = []
        for filename in os.listdir('strategies'):
            if filename.endswith('.json'):
                try:
                    with open(f"strategies/{filename}", 'r') as f:
                        data = json.load(f)
                        data['filename'] = filename
                        strategies.append(data)
                except:
                    continue
                    
        # Sort by fitness score
        strategies.sort(key=lambda x: x['fitness'], reverse=True)
        
        print("\nSaved Strategies:")
        print("-" * 80)
        for strategy in strategies:
            print(f"File: {strategy['filename']}")
            print(f"Fitness: {strategy['fitness']:.2f}")
            print(f"Created: {strategy['timestamp']}")
            print(f"Board Size: {strategy['board_size']}")
            print("-" * 80)
            
        return strategies

    def _initialize_population(self) -> List[Dict[str, float]]:
        """Initialize population with random strategy parameters"""
        population = []
        for _ in range(self.population_size):
            strategy = {
                'hit_weight': random.uniform(1.0, 3.0),
                'pattern_weight': random.uniform(1.0, 2.0),
                'density_weight': random.uniform(0.8, 1.5),
                'edge_weight': random.uniform(0.5, 1.2),
                'exploration_rate': random.uniform(0.1, 0.3)
            }
            population.append(strategy)
        return population

    def _fitness(self, strategy: Dict[str, float]) -> float:
        """Evaluate fitness of a strategy by playing games"""
        total_moves = 0
        num_games = 3  # Number of games to evaluate each strategy
        
        for _ in range(num_games):
            game = BattleshipGame()
            moves = self.play_game(strategy, game)
            total_moves += len(moves)
        
        # Lower number of moves = higher fitness
        return 1000.0 / (total_moves / num_games)

    def _crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Dict[str, float]:
        """Perform crossover between two parent strategies"""
        child = {}
        for key in parent1.keys():
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child

    def _mutate(self, strategy: Dict[str, float]) -> Dict[str, float]:
        """Mutate strategy parameters"""
        mutated = strategy.copy()
        for key in mutated:
            if random.random() < self.mutation_rate:
                # Add or subtract up to 20% of the current value
                change = random.uniform(-0.2, 0.2) * mutated[key]
                mutated[key] = max(0.1, mutated[key] + change)
        return mutated

    def _calculate_cell_probability(self, x: int, y: int, strategy: Dict[str, float]) -> float:
        """Calculate probability for a cell based on current strategy"""
        if (x, y) in self.hits or (x, y) in self.misses:
            return 0.0

        prob = 0.0
        
        # Adjacent to hits
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_x, new_y = x + dx, y + dy
            if (new_x, new_y) in self.unconfirmed_hits:
                prob += strategy['hit_weight']

        # Checkerboard pattern
        if (x + y) % 2 == 0:
            prob += strategy['pattern_weight']

        # Ship density
        density = self._calculate_ship_density(x, y)
        prob += density * strategy['density_weight']

        # Edge preference
        if x in [0, self.board_size-1] or y in [0, self.board_size-1]:
            prob += strategy['edge_weight']

        return prob

    def _calculate_ship_density(self, x: int, y: int) -> float:
        """Calculate how many ships could potentially cover this cell"""
        density = 0
        for ship_length in self.remaining_ships.values():
            # Horizontal check
            for start_y in range(max(0, y - ship_length + 1), min(y + 1, self.board_size - ship_length + 1)):
                valid = True
                for j in range(start_y, start_y + ship_length):
                    if (x, j) in self.misses or (x, j) in self.sunk_ship_positions:
                        valid = False
                        break
                if valid:
                    density += 1

            # Vertical check
            for start_x in range(max(0, x - ship_length + 1), min(x + 1, self.board_size - ship_length + 1)):
                valid = True
                for i in range(start_x, start_x + ship_length):
                    if (i, y) in self.misses or (i, y) in self.sunk_ship_positions:
                        valid = False
                        break
                if valid:
                    density += 1

        return density / len(self.remaining_ships)

    def get_next_target(self, strategy: Dict[str, float]) -> Tuple[int, int]:
        """Get next target based on current strategy"""
        if random.random() < strategy['exploration_rate']:
            # Random exploration
            valid_targets = [(i, j) for i in range(self.board_size) 
                           for j in range(self.board_size)
                           if (i, j) not in self.hits and (i, j) not in self.misses]
            return random.choice(valid_targets)

        # Calculate probabilities for all cells
        prob_map = np.zeros((self.board_size, self.board_size))
        for i in range(self.board_size):
            for j in range(self.board_size):
                prob_map[i][j] = self._calculate_cell_probability(i, j, strategy)

        # Get highest probability cell
        max_prob = np.max(prob_map)
        if max_prob > 0:
            candidates = [(i, j) for i, j in zip(*np.where(prob_map == max_prob))
                         if (i, j) not in self.hits and (i, j) not in self.misses]
            return random.choice(candidates)

        # Fallback to random valid target
        valid_targets = [(i, j) for i in range(self.board_size) 
                        for j in range(self.board_size)
                        if (i, j) not in self.hits and (i, j) not in self.misses]
        return random.choice(valid_targets)

    def play_game(self, strategy: Dict[str, float], game: BattleshipGame) -> List[Tuple[int, int, bool]]:
        """Play a complete game using given strategy"""
        self.hits.clear()
        self.misses.clear()
        self.remaining_ships = self.ships.copy()
        self.unconfirmed_hits.clear()
        self.sunk_ship_positions.clear()
        
        moves = []
        while True:
            x, y = self.get_next_target(strategy)
            is_hit = game.check_hit(x, y)
            
            if is_hit:
                self.hits.add((x, y))
                self.unconfirmed_hits.add((x, y))
                hit_ship = None
                for ship in game.ships:
                    if (x, y) in ship.positions:
                        ship.hits.add((x, y))
                        hit_ship = ship
                        if hit_ship.is_sunk():
                            self.sunk_ship_positions.update(hit_ship.positions)
                            self.unconfirmed_hits -= set(hit_ship.positions)
                            for ship_name, length in list(self.remaining_ships.items()):
                                if length == len(hit_ship.positions):
                                    del self.remaining_ships[ship_name]
                                    break
            else:
                self.misses.add((x, y))
            
            moves.append((x, y, is_hit))
            
            if all(ship.is_sunk() for ship in game.ships):
                break
                
        return moves

    def evolve(self, save_best: bool = True):
        """Run the genetic algorithm to evolve optimal strategy
        
        Parameters
        ----------
        save_best : bool, optional
            Whether to automatically save the best strategy after evolution
        """
        best_per_generation = []
        
        for generation in range(self.generations):
            # Evaluate fitness for each strategy
            fitness_scores = [(strategy, self._fitness(strategy)) 
                            for strategy in self.population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Store best strategy
            if fitness_scores[0][1] > self.best_fitness:
                self.best_strategy = fitness_scores[0][0]
                self.best_fitness = fitness_scores[0][1]
            
            best_per_generation.append(self.best_fitness)
            
            # Print progress
            avg_fitness = sum(score for _, score in fitness_scores) / len(fitness_scores)
            print(f"Generation {generation + 1}/{self.generations}")
            print(f"Best Fitness: {self.best_fitness:.2f}")
            print(f"Average Fitness: {avg_fitness:.2f}")
            
            # Selection and population update
            elite = [strategy for strategy, _ in fitness_scores[:self.elite_size]]
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                tournament_size = 5
                tournament = random.sample(fitness_scores, tournament_size)
                parent1 = max(tournament, key=lambda x: x[1])[0]
                tournament = random.sample(fitness_scores, tournament_size)
                parent2 = max(tournament, key=lambda x: x[1])[0]
                
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            self.population = new_population
        
        print("\nEvolution completed!")
        print(f"Best fitness achieved: {self.best_fitness:.2f}")
        
        if save_best:
            self.save_strategy()

def test_genetic_ai():
    # Initialize and evolve the genetic AI
    ai = GeneticBattleshipAI(population_size=1000, generations=100)
    
    # # Option 1: Evolve new strategy
    # print("Evolving new strategy...")
    # ai.evolve(save_best=True)
    
    # Option 2: Load existing strategy
    print("Loading existing strategy...")
    # ai.list_saved_strategies()
    ai.load_strategy("4.json")
    
    # Test the strategy
    print("\nTesting strategy...")
    total_moves = 0
    num_games = 100
    
    for i in range(num_games):
        game = BattleshipGame()
        moves = ai.play_game(ai.best_strategy, game)
        print(game.get_board_display(show_ships=True))
        print(f"Game {i+1} completed in {len(moves)} moves")
        total_moves += len(moves)
        print(moves)
    
    avg_moves = total_moves / num_games
    print(f"\nAverage moves per game: {avg_moves:.2f}")
    print("Strategy parameters:", ai.best_strategy)

if __name__ == "__main__":
    test_genetic_ai()