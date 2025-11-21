import neat
import numpy as np
import sys
import os
# Add parent directory to path to import neato_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neato_client
import time
import pickle
import cv2

class Substrate:
    def __init__(self, width=128, height=112):
        self.width = width
        self.height = height
        
        # Generate coordinate grids (normalized -1 to 1)
        # Shape: (height, width)
        x_range = np.linspace(-1, 1, width)
        y_range = np.linspace(-1, 1, height)
        self.input_x, self.input_y = np.meshgrid(x_range, y_range)
        
        # Flatten to (N, 1)
import neat
import numpy as np
import sys
import os
# Add parent directory to path to import neato_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neato_client
import time
import pickle
import cv2

class Substrate:
    def __init__(self, width=128, height=112):
        self.width = width
        self.height = height
        
        # Generate coordinate grids (normalized -1 to 1)
        # Shape: (height, width)
        x_range = np.linspace(-1, 1, width)
        y_range = np.linspace(-1, 1, height)
        self.input_x, self.input_y = np.meshgrid(x_range, y_range)
        
        # Flatten to (N, 1)
        self.input_coords = np.column_stack((self.input_x.flatten(), self.input_y.flatten()))
        
        # Define Output Coordinates (Buttons)
        # We place them in a geometric arrangement to give the AI spatial hints
        # e.g., Left is to the left of Right
        self.buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
        # Run 2: Added 'Y' for Running/Shooting
        self.active_buttons = ['B', 'Y', 'Left', 'Right', 'A']
        
        # Manually define positions for active buttons in a circle or line
        # Let's put them in a line at z=1 (if we had 3D) or just separate them
        # For 2D CPPN, we just give them (x, y) coords.
        # Let's place them at y=1 (bottom of "screen" conceptually) and spread across x
        self.output_coords = []
        num_outputs = len(self.active_buttons)
        for i in range(num_outputs):
            x = -1 + (2.0 * i / (num_outputs - 1))
            y = 1.0 # "Output layer" position
            self.output_coords.append([x, y])
        self.output_coords = np.array(self.output_coords)
        
        # Run 2: Input Feedback (Memory)
        # We add virtual input coordinates for the previous state of each button
        # Let's place them at y=-1.2 (below the screen inputs)
        self.feedback_coords = []
        for i in range(num_outputs):
            x = -1 + (2.0 * i / (num_outputs - 1))
            y = -1.2 
            self.feedback_coords.append([x, y])
        self.feedback_coords = np.array(self.feedback_coords)
        
        # Combine screen inputs and feedback inputs
        # Screen: (N_pixels, 2)
        # Feedback: (N_buttons, 2)
        self.all_input_coords = np.vstack((self.input_coords, self.feedback_coords))

    def build_phenotype(self, cppn, config):
        """
        Constructs the weight matrix from Input -> Output using the CPPN.
        Returns a function that takes an image and returns button probabilities.
        """
        # We need to query CPPN for every pair of (Input, Output)
        # Input: (N_pixels + N_buttons, 2)
        # Output: (N_buttons, 2)
        # Total weights: N_pixels * N_buttons
        
        # Broadcast inputs and outputs to create all pairs
        # This can be memory intensive. Let's do it per output neuron to save memory.
        
        # Weights shape: (N_inputs, N_outputs)
        weights = np.zeros((self.all_input_coords.shape[0], self.output_coords.shape[0]))
        
        for i in range(self.output_coords.shape[0]):
            out_x, out_y = self.output_coords[i]
            # print(f"Building weights for Output {i+1}/{self.output_coords.shape[0]}...")
            
            # Create inputs for CPPN: x1, y1, x2, y2
            # x1, y1 are all input pixels
            # x2, y2 are constant for this output neuron
            
            # We can batch query the CPPN if it supports it, but neat-python CPPN is usually node-by-node.
            # However, neat-python's FeedForwardNetwork.activate is for a single input vector.
            # We need to iterate. This is the slow part of HyperNEAT construction.
            # Optimization: The CPPN is usually small.
            
            for j in range(self.all_input_coords.shape[0]):
                in_x, in_y = self.all_input_coords[j]
                # Query CPPN
                # Inputs: x1, y1, x2, y2
                w = cppn.activate([in_x, in_y, out_x, out_y])[0]
                weights[j, i] = w
                
        return weights

class NeatoBrain:
    def __init__(self):
        self.substrate = Substrate()
        self.bridge = neato_client.NeatoBridge()
        
    def evaluate(self, genomes, config):
        """
        Evaluates a population of genomes.
        """
        for genome_id, genome in genomes:
            # 1. Build CPPN
            cppn = neat.nn.FeedForwardNetwork.create(genome, config)
            
            # 2. Build Phenotype (Weight Matrix)
            # This maps (14k pixels + 5 feedback) -> 5 buttons
            weights = self.substrate.build_phenotype(cppn, config)
            
            # 3. Run Game
            fitness = self.run_simulation(weights)
            genome.fitness = fitness
            print(f"Genome {genome_id} Fitness: {fitness}")

    def run_simulation(self, weights):
        """
        Runs the game for a single agent.
        """
        # Connect if not already connected
        if not self.bridge.sock:
            if not self.bridge.connect():
                print("Could not connect to bridge!")
                return 0
            
        # Always reset to save state at start of each genome evaluation
        self.bridge.reset()
        time.sleep(0.5)  # Give save state time to load
        
        # Read initial state to verify we're in the level
        img = self.bridge.get_state()
        if img is None:
            print("Failed to get initial state!")
            return 0
        
        initial_x = self.bridge.mario_x
        # print(f"  Starting position: X={initial_x}")
        
        # Initial State
        max_frames = 600 # 10 seconds limit to start
        current_frame = 0
        max_distance = initial_x  # Start from actual initial position
        stagnation_counter = 0
        right_press_count = 0  # Track how many frames RIGHT was pressed
        
        # Run 2: Initialize previous button states (all off)
        prev_buttons_vector = np.zeros(len(self.substrate.active_buttons))
        
        while current_frame < max_frames:
            # 1. Get Input
            # We need the raw image. The bridge returns it via get_state()
            # but get_state also updates metadata.
            # We need to access the image data directly or modify get_state to return it.
            # Currently get_state returns the image.
            img = self.bridge.get_state()
            
            if img is None:
                break
                
            # Flatten image to (N,)
            # Convert to grayscale for simplicity first? Or keep RGB?
            # Let's do Grayscale to save weights (14k vs 42k)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            screen_inputs = (img_gray.flatten() / 127.5) - 1.0  # Normalize to -1 to 1
            
            # Combine screen inputs with previous button states (Feedback)
            # Feedback inputs should also be normalized -1 to 1? 
            # Let's say 1.0 is pressed, -1.0 is not pressed.
            feedback_inputs = (prev_buttons_vector * 2.0) - 1.0
            
            inputs = np.concatenate((screen_inputs, feedback_inputs))
            
            # 2. Activate Network (Matrix Mult)
            # (1, N) dot (N, Outputs) = (1, Outputs)
            outputs = np.dot(inputs, weights)
            
            # 3. Decide Buttons (Sigmoid activation)
            # Sigmoid ranges from 0 to 1, threshold at 0.5
            outputs = 1 / (1 + np.exp(-outputs))
            
            buttons = {}
            # Update prev_buttons_vector for next frame
            new_buttons_vector = np.zeros(len(self.substrate.active_buttons))
            
            for i, btn_name in enumerate(self.substrate.active_buttons):
                is_pressed = outputs[i] > 0.5
                buttons[btn_name] = is_pressed
                new_buttons_vector[i] = 1.0 if is_pressed else 0.0
            
            prev_buttons_vector = new_buttons_vector
                
            # Prevent conflicting directional inputs
            
            # Prevent conflicting directional inputs
            # Left+Right cancel each other out in SNES
            if buttons.get('Left') and buttons.get('Right'):
                # Keep the one with stronger output
                left_idx = self.substrate.active_buttons.index('Left')
                right_idx = self.substrate.active_buttons.index('Right')
                if abs(outputs[left_idx]) > abs(outputs[right_idx]):
                    buttons['Right'] = False
                else:
                    buttons['Left'] = False
                
            # 4. Send Action
            self.bridge.act(buttons)
            
            # Track Right presses for exploration bonus
            if buttons.get('Right', False):
                right_press_count += 1
            
            # 5. Check Fitness
            # Simple fitness: Max X position
            current_distance = self.bridge.mario_x
            if current_distance > max_distance:
                max_distance = current_distance
                stagnation_counter = 0
            else:
                stagnation_counter += 1
                
            # Early exit if stuck
            if stagnation_counter > 60: # 1 second stuck
                break
                
            current_frame += 1
        
        # Calculate fitness
        # Run 2: Velocity Bonus
        # If he moved far in few frames, that's good.
        # Average speed = Distance / Time
        distance_traveled = max_distance - initial_x
        if current_frame > 0:
            avg_speed = distance_traveled / current_frame
        else:
            avg_speed = 0
            
        # Bonus: 10 points per pixel/frame of speed
        velocity_bonus = avg_speed * 10.0
        
        # Exploration bonus (still good to keep)
        right_press_bonus = 1.0 * right_press_count
            
        return max_distance + right_press_bonus + velocity_bonus

def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Run 2: Checkpointing
    # Check for existing checkpoint
    # Look for files starting with neat-checkpoint-
    checkpoint_files = [f for f in os.listdir('.') if f.startswith('neat-checkpoint-')]
    if checkpoint_files:
        # Find the latest one
        # Format is neat-checkpoint-GENERATION
        latest_checkpoint = max(checkpoint_files, key=lambda x: int(x.split('-')[-1]))
        print(f"Resuming from checkpoint: {latest_checkpoint}")
        p = neat.Checkpointer.restore_checkpoint(latest_checkpoint)
    else:
        print("Starting new population...")
        p = neat.Population(config)
    
    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Save checkpoint every 5 generations
    p.add_reporter(neat.Checkpointer(5))
    
    brain = NeatoBrain()
    winner = p.run(brain.evaluate, 50) # Run for 50 generations this time
    
    # Save winner
    with open('winner_run2.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    # If run directly, assume we are in the runs/ directory or root?
    # Let's assume root for consistency with main.py
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configs', 'config-run2')
    run(config_path)
