# Neato: General Video Game AI Agent

Neato is an AI agent designed to learn how to play video games through neuroevolution. Inspired by SethBling's MarI/O, Neato aims to go further by using **HyperNEAT** for high-fidelity visual processing and a **Python-based brain** to leverage modern machine learning capabilities.

## The Goal
To create a general-purpose game player that can:
1.  **See** the entire screen (not just a small grid).
2.  **Learn** from scratch without human rules.
3.  **Generalize** across different levels and situations.
4.  **Play** any SNES game (starting with Super Mario World).

## Architecture
Neato consists of two main components connected by a TCP socket bridge:

1.  **The Body (Bizhawk Emulator)**: Runs the game and executes a Lua script (`neato_bridge.lua`) that acts as a server. It exports the screen state and accepts controller inputs.
2.  **The Brain (Python)**: A Python application (`neato_client.py` + Brain) that connects to the emulator. It uses **HyperNEAT** (Hypercube-based NeuroEvolution of Augmenting Topologies) to evolve neural networks that can process the geometric patterns of the game screen.

## Setup

### Prerequisites
- **Bizhawk Emulator**: [Download here](https://tasvideos.org/BizHawk)
- **Python 3.8+**
- **SNES ROM** (e.g., Super Mario World)

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/LeePresswood/neato.git
    cd neato
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
1.  Open **Bizhawk** and load your ROM.
2.  Open the **Lua Console** (`Tools > Lua Console`).
3.  Load the script `neato_bridge.lua`. You should see "Server started".
4.  Run the Python client:
    ```bash
    python neato_client.py
    ```

## 🗺️ Roadmap

For a detailed technical breakdown, please see the [Implementation Plan](implementation_plan.md) and [Design Overview](design_overview.md).

### Phase 1: The Foundation (✅ Completed)
- [x] **Bridge Construction**: Established TCP socket communication between Bizhawk (Lua) and Python.
- [x] **Basic Control**: Implemented command structure to send button presses to the emulator.
- [x] **State Retrieval**: Created protocol for Python to request game state from Lua.

### Phase 2: The Senses (✅ Completed)
- [x] **Vision System**: Implemented high-fidelity screen capture using `mss` and `opencv`.
- [x] **Geometry Tuning**: Calibrated capture window to perfectly crop the game screen, removing window borders and UI elements.
- [x] **Proprioception**: Implemented memory reading to track Mario's X/Y coordinates, Game Mode, Level Index, and Animation State.

### Phase 3: The Brain (🚧 In Progress)
- [ ] **HyperNEAT Integration**: Setting up the `neat-python` configuration and CPPN substrate.
- [ ] **Fitness Function**: Defining the "score" based on distance traveled, speed, and level completion.
- [ ] **Training Loop**: Creating the main evolutionary loop to train generations of agents.

### Phase 4: The Evolution (🔮 Future)
- [ ] **Species Stagnation Handling**: Implementing strategies to break out of local optima.
- [ ] **Save State Randomization**: Training on multiple levels to ensure generalized learning.
- [ ] **Media Pipeline**: Automated recording of best-performing agents for YouTube/GitHub showcases.

## Credits
- Inspired by [SethBling's MarI/O](https://www.youtube.com/watch?qv6i66pLzQ)
- Built with [NEAT-Python](https://neat-python.readthedocs.io/)
