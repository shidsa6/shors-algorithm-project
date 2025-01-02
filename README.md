# Shor's Algorithm Project

This project demonstrates the implementation of Shor's Algorithm, a quantum algorithm used for integer factorization. The purpose of the project is to represent the basic logic of the algorithm, implement simple examples, and provide visualizations to help understand its key components.

## Project Structure

### Files

- **shor_algorithm.py**: Contains the main implementation of Shor's Algorithm, including:
  - Modular exponentiation function.
  - Quantum Fourier Transform (QFT) implementation.
  - The main function to execute Shor's Algorithm and extract factors.

- **visualize_circuit.py**: Provides visualizations of the quantum circuit and plots the probability distribution of measurement outcomes. Includes:
  - Functions to create and display Shor's Algorithm circuits.
  - Probability peak plotting with realistic period markers.

- **test_shor_algorithm.py**: Unit tests for validating the correctness of Shor's Algorithm implementation.

- **requirements.txt**: Lists all dependencies required to run the project.

- **LICENSE**: The license file for the project.

- **outputs/**: A directory that stores generated output files:
  - `shor_circuit.png`: Visualization of the quantum circuit.
  - `probability_peaks.png`: Histogram showing the probability distribution of measurement outcomes.

### Graphs

1. **Circuit Diagram**: A clear representation of the Shor's Algorithm quantum circuit, highlighting key stages such as:
   - Application of Hadamard gates.
   - Controlled modular exponentiation.
   - Inverse QFT.

   Example: `shor_circuit.png`

2. **Probability Peaks**: A histogram displaying the probability of measured phases. The red dashed lines indicate expected periodicity based on the algorithm's results. This helps visualize the quantum period-finding process and highlights key phases contributing to factorization. Note that these graphs demonstrate probabilities and are best interpreted with multiple runs to mitigate probabilistic noise.

   Example: `probability_peaks.png`

## Important Notes

- The project simulates Shor's Algorithm using Qiskit's classical simulator backend. For more accurate and realistic results, especially for the Quantum Fourier Transform (QFT) step, using an actual quantum computer is recommended.

- Due to the probabilistic nature of quantum algorithms, outputs may vary between runs. For more consistent results, increase the number of shots or run the simulation multiple times.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. To run Shor's Algorithm:
   ```bash
   python shor_algorithm.py
   ```

2. To visualize the circuit and probability peaks:
   ```bash
   python visualize_circuit.py
   ```

3. To run unit tests:
   ```bash
   python -m unittest test_shor_algorithm.py
   ```

## License

This project is licensed under the terms of the LICENSE file included in the repository.

---

Feel free to reach out with any questions or suggestions for improvements!
