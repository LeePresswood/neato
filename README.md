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

## Roadmap
- [x] **Phase 1: Foundation**: Establish communication between Bizhawk (Lua) and Python.
- [ ] **Phase 2: Vision**: Implement high-fidelity screen capture and processing.
- [ ] **Phase 3: Evolution**: Implement the HyperNEAT algorithm and training loop.
- [ ] **Phase 4: Generalization**: Add multi-state training and novelty search.

## Credits
- Inspired by [SethBling's MarI/O](https://www.youtube.com/watch?qv6i66pLzQ)
- Built with [NEAT-Python](https://neat-python.readthedocs.io/)
