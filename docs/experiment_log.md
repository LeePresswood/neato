# Neato Experiment Log

This document tracks the progress of the Neato AI training experiments. We record the configuration, results, and key observations (positives/negatives) for each run to guide future improvements.

## Run #1: The Awakening (Current)

**Date**: 2025-11-21
**Goal**: Achieve basic movement and verify the pipeline.

### Configuration
- **Input**: 128x112 Grayscale (downsampled)
- **Brain**: HyperNEAT (CPPN with Tanh activation)
- **Outputs**: 4 Buttons (`B`, `Left`, `Right`, `A`)
- **Fitness**: Max X Distance + (1.0 * Right Press Count)
- **Population**: 20
- **Generations**: 10 (Target)

### Results (Mid-Run)
- **Best Fitness**: ~4075 (Generation 2)
- **Est. Distance**: ~3400 pixels (Level 1 is long!)

### Observations

**Positives (+)**
- **It Works!**: The "stuck at start" bug is definitively fixed.
- **Exploration Bonus**: The +1.0 reward for pressing `Right` successfully bootstrapped the learning. The agents quickly learned that `Right` = `Points`.
- **Tanh Activation**: Switching to `tanh` was critical. It allowed the network to output positive values (press button) even when the screen input was mostly negative (black/dark pixels).
- **Speed**: Evolution happened very fast (Gen 0 -> Gen 2 saw massive jump).

**Negatives / Unknowns (-)**
- **One-Trick Pony?**: Is it *only* holding Right? We need to see if it learns to Jump (`A`) or Run (`B`) to clear obstacles.
- **Vision Usage**: Is it actually looking at the screen, or just optimizing the bias to always press Right? (HyperNEAT *should* use the screen, but early fitness spikes can sometimes be blind optimizations).
- **Stuck Logic**: The "stuck for 60 frames" rule might be too strict for complex obstacles.

### Next Steps for Run #2
- **Visual Debugging**: We need to *see* the gameplay. (Need to implement the replay/recording system).
- **Fitness Tuning**: If he gets stuck at a pipe, we might need to reward Y-movement (jumping) or penalize standing still more aggressively.
