# CLA_Hspice_Generator

A Python toolkit for generating Carry Look-Ahead (CLA) adder circuit descriptions/netlists, stimulus vectors, and HSPICE simulation files.

## Repository Structure

- `main.py` — Entry point orchestrating CLA generation, test vector creation, and HSPICE file output.
- `Primitives.py` — Definitions and builders for fundamental logic/circuit building blocks (e.g., gates, propagate/generate blocks, carry logic, or subcircuits).
- `hspice_files/` — Directory for generated or reference HSPICE netlists, stimulus/simulation decks, and outputs.
- `vector_files/` — Directory for input/expected test vectors used to drive and verify simulations.
- `.gitignore` — Specifies ignored build, simulation, or temporary files.

## Getting Started

### Prerequisites

- **Python 3.x**
- **HSPICE** (or a compatible SPICE simulator) if running generated circuit simulations.

### Usage

1. Clone the repository:
   ```bash
   git clone [https://github.com/sadra-ghavami/CLA_Hspice_Generator.git](https://github.com/sadra-ghavami/CLA_Hspice_Generator.git)
   cd CLA_Hspice_Generator
