# Project Neato - Implementation Plan

## Goal Description
Develop "Neato", a general-purpose video game AI agent capable of playing SNES games (and eventually others) via the Bizhawk emulator. The system will improve upon SethBling's MarI/O by using high-fidelity visual inputs (HyperNEAT), generalized training across multiple game states, and a robust Python-based machine learning backend.

## User Review Required
> [!IMPORTANT]
> **Architecture Choice**: We are choosing a **Python-centric** approach. Unlike SethBling's pure Lua script, we will run the "Brain" in Python (using libraries like PyTorch or NEAT-Python) and use Lua only to interface with the emulator. This allows us to use modern hardware acceleration (GPUs) and advanced algorithms.

> [!NOTE]
> **HyperNEAT**: To handle the "high fidelity" requirement (thousands of pixel inputs), we will use **HyperNEAT**. Standard NEAT struggles to evolve networks with thousands of inputs. HyperNEAT evolves a pattern-generating network (CPPN) that "paints" the weights of the playing network, allowing it to understand the geometry of the screen.

## Proposed Changes

### 1. The Bridge (Communication Layer)
We need a robust communication channel between the Bizhawk Emulator (running Lua) and our AI Brain (running Python).

#### [NEW] `neato_bridge.lua`
- **Role**: Server (runs inside Bizhawk).
- **Features**:
    - Opens a TCP socket on localhost.
    - **Commands**:
        - `GET_STATE`: Returns screen pixels (or RAM grid) and game variables (Mario's X, Y, State).
        - `ACT`: Accepts a button mask (e.g., "Press A and Right") and advances the frame.
        - `LOAD_STATE`: Loads a specific save state (for generalized training).
        - `RESET`: Soft or hard resets the console.

#### [NEW] `neato_client.py`
- **Role**: Client (Python).
- **Features**:
    - Connects to `neato_bridge.lua`.
    - Implements a `Gym`-like interface: `observation, reward, done, info = env.step(action)`.
    - Handles data serialization/deserialization (JSON or binary for speed).

### 2. The Brain (AI Core)
The core logic that evolves and plays the game.

#### [NEW] `neato_brain.py`
- **Algorithm**: **HyperNEAT** (Hypercube-based NeuroEvolution of Augmenting Topologies).
- **Libraries**: `neat-python` (base) + `pureples` (HyperNEAT extension) or a custom PyTorch implementation.
- **Inputs**:
    - **Visual Substrate**: A 2D grid representing the screen (e.g., downsampled to 64x64 or 128x112).
    - **State Substrate**: Optional extra inputs for bias or specific memory values.
- **Outputs**:
    - **Controller Substrate**: Output nodes corresponding to SNES buttons (A, B, X, Y, L, R, Start, Select, D-Pad).

### 3. Training Pipeline (The Gym)
The loop that manages the evolution process.

#### [NEW] `trainer.py`
- **Population Management**: Handles the NEAT population (species, genomes).
- **Evaluation Loop**:
    - For each genome in the population:
        - **Generalization Check**: Instead of running just Level 1-1, pick $K$ random save states from a `training_set` folder.
        - Run the agent in each state for $T$ seconds.
        - **Fitness Function**: Calculate fitness based on progress (distance right), score, or novelty (exploring new areas).
        - Aggregate fitness (e.g., average or minimum performance across all states to ensure robustness).
- **Checkpointing**: Saves the best genomes and the current population state.

### 4. Media Capture Pipeline (The Cameraman)
To document progress and create content for YouTube.
# Project Neato - Implementation Plan

## Goal Description
Develop "Neato", a general-purpose video game AI agent capable of playing SNES games (and eventually others) via the Bizhawk emulator. The system will improve upon SethBling's MarI/O by using high-fidelity visual inputs (HyperNEAT), generalized training across multiple game states, and a robust Python-based machine learning backend.

## User Review Required
> [!IMPORTANT]
> **Architecture Choice**: We are choosing a **Python-centric** approach. Unlike SethBling's pure Lua script, we will run the "Brain" in Python (using libraries like PyTorch or NEAT-Python) and use Lua only to interface with the emulator. This allows us to use modern hardware acceleration (GPUs) and advanced algorithms.

> [!NOTE]
> **HyperNEAT**: To handle the "high fidelity" requirement (thousands of pixel inputs), we will use **HyperNEAT**. Standard NEAT struggles to evolve networks with thousands of inputs. HyperNEAT evolves a pattern-generating network (CPPN) that "paints" the weights of the playing network, allowing it to understand the geometry of the screen.

## Proposed Changes

### 1. The Bridge (Communication Layer)
We need a robust communication channel between the Bizhawk Emulator (running Lua) and our AI Brain (running Python).

#### [NEW] `neato_bridge.lua`
- **Role**: Server (runs inside Bizhawk).
- **Features**:
    - Opens a TCP socket on localhost.
    - **Commands**:
        - `GET_STATE`: Returns screen pixels (or RAM grid) and game variables (Mario's X, Y, State).
        - `ACT`: Accepts a button mask (e.g., "Press A and Right") and advances the frame.
        - `LOAD_STATE`: Loads a specific save state (for generalized training).
        - `RESET`: Soft or hard resets the console.

#### [NEW] `neato_client.py`
- **Role**: Client (Python).
- **Features**:
    - Connects to `neato_bridge.lua`.
    - Implements a `Gym`-like interface: `observation, reward, done, info = env.step(action)`.
    - Handles data serialization/deserialization (JSON or binary for speed).

### 2. The Brain (AI Core)
The core logic that evolves and plays the game.

#### [NEW] `neato_brain.py`
- **Algorithm**: **HyperNEAT** (Hypercube-based NeuroEvolution of Augmenting Topologies).
- **Libraries**: `neat-python` (base) + `pureples` (HyperNEAT extension) or a custom PyTorch implementation.
- **Inputs**:
    - **Visual Substrate**: A 2D grid representing the screen (e.g., downsampled to 64x64 or 128x112).
    - **State Substrate**: Optional extra inputs for bias or specific memory values.
- **Outputs**:
    - **Controller Substrate**: Output nodes corresponding to SNES buttons (A, B, X, Y, L, R, Start, Select, D-Pad).

### 3. Training Pipeline (The Gym)
The loop that manages the evolution process.

#### [NEW] `trainer.py`
- **Population Management**: Handles the NEAT population (species, genomes).
- **Evaluation Loop**:
    - For each genome in the population:
        - **Generalization Check**: Instead of running just Level 1-1, pick $K$ random save states from a `training_set` folder.
        - Run the agent in each state for $T$ seconds.
        - **Fitness Function**: Calculate fitness based on progress (distance right), score, or novelty (exploring new areas).
        - Aggregate fitness (e.g., average or minimum performance across all states to ensure robustness).
- **Checkpointing**: Saves the best genomes and the current population state.

### 4. Media Capture Pipeline (The Cameraman)
To document progress and create content for YouTube.

#### [NEW] `media_manager.py`
- **Automated Screenshots**:
    - Capture "Milestone Moments" (e.g., first time passing x=1000).
    - Save the "Network View" (visualizing the brain's activations) as images.
- **Replay Recording**:
    - At the end of every $N$ generations, automatically run the "Best Genome" in a special "Showcase Mode".
    - Trigger Bizhawk to dump a video file or sequence of screenshots for that run.
- **Gif Generation**:
    - Compile the Python-side visualization (what the AI sees) into GIFs for the GitHub README.



## Project Restructuring (Multi-Run Support)

### Goal
Preserve the code and configuration for each "Run" separately to document the evolution of the AI.

### Changes
#### [NEW] `runs/` Directory
- Will contain the specific logic for each experiment.
- **`runs/run1_awakening.py`**: Snapshot of the current successful "Run 1" code.
- **`runs/run2_runner.py`**: The new code for "Run 2" (with Y button and memory).
- **`runs/configs/`**: Directory to store NEAT config files for each run.

#### [NEW] `main.py`
- Central entry point.
- Usage: `python main.py run1` or `python main.py run2`.
- dynamically imports and executes the requested run module.

#### [MODIFY] `neato_brain.py`
- Will be deprecated/removed or turned into a shared library `neato_core.py` if we decide to share code.
- For now, we will copy it to `runs/run1_awakening.py` to preserve it.

## Run 2: The Runner (Planned)

### Goal
Enable Mario to perform complex movement actions: **Running** (holding Y) and **High Jumping** (holding B).

### 1. Button Holding & Memory
**Problem**: The current "one input per frame" feed-forward brain has no memory. It cannot decide to "keep holding" a button based on previous state.
**Solution**: **Input Feedback Loop**.
- Add the previous frame's button states as **inputs** to the network in the next frame.
- **New Inputs**: `Prev_B`, `Prev_Y`, `Prev_Left`, `Prev_Right`, `Prev_A`
- This allows the network to learn rules like: "If I was pressing Jump, and I'm still in the air, keep pressing Jump."

### 2. Running Capability
**Problem**: Mario moves slowly. To clear large gaps, he needs to run.
**Solution**: Add `Y` button to the active set.
- **Active Buttons**: `B` (Jump), `Y` (Run), `Left`, `Right`, `A` (Spin)

### 3. Fitness Tuning
**Problem**: Current fitness only rewards distance.
**Solution**:
- **Velocity Bonus**: Reward moving *fast* (requires running).
- **Jump Penalty**: Slight penalty for jumping to prevent "bunny hopping" unless necessary? (Maybe wait on this).

## Verification Plan

### Automated Tests
- **Bridge Test**: A script that connects to Bizhawk, sends random button presses, and verifies that the screen changes (pixel diff).
- **XOR Test**: Verify the HyperNEAT implementation can solve a simple XOR problem before hooking it up to the game.

### Manual Verification
- **Visual Inspection**: Watch the agent play in real-time via the Bizhawk window.
- **Overlay**: Draw the agent's "thoughts" (input activation) on the screen using Lua GUI functions to see what it's looking at.
