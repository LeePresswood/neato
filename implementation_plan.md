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

## Verification Plan

### Automated Tests
- **Bridge Test**: A script that connects to Bizhawk, sends random button presses, and verifies that the screen changes (pixel diff).
- **XOR Test**: Verify the HyperNEAT implementation can solve a simple XOR problem before hooking it up to the game.

### Manual Verification
- **Visual Inspection**: Watch the agent play in real-time via the Bizhawk window.
- **Overlay**: Draw the agent's "thoughts" (input activation) on the screen using Lua GUI functions to see what it's looking at.
