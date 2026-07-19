# Shor's Algorithm Project

This project implements Shor's Algorithm, a quantum algorithm for integer factorization, including the full quantum period-finding subroutine: controlled modular exponentiation via explicit unitary construction, an inverse Quantum Fourier Transform, and continued-fraction-based period extraction from the measured phases (not a classical fallback dressed up as a quantum circuit). The purpose of the project is to provide a genuine, independently-verifiable implementation with visualizations to help understand its key components.

## Project Structure

### Files

- **shor_algorithm.py**: Contains the main implementation of Shor's Algorithm, including:
  - Modular exponentiation function.
  - Quantum Fourier Transform (QFT) implementation.
  - The main function to execute Shor's Algorithm and extract factors.

- **visualize_circuit.py**: Provides visualizations of the quantum circuit and plots the probability distribution of measurement outcomes. Includes:
  - Functions to create and display Shor's Algorithm circuits.
  - Probability peak plotting with realistic period markers.

- **tests/test_shor_algorithm.py**: Unit tests for validating the correctness of Shor's Algorithm implementation, including regression checks that the inverse QFT is a true inverse and that controlled modular multiplication performs the correct permutation.

- **requirements.txt**: Lists all dependencies required to run the project.

- **LICENSE**: The license file for the project.

- **examples/**: A directory that stores generated output files:
  - `shor_circuit.png`: Visualization of the quantum circuit.
  - `probability_peaks.png`: Histogram showing the probability distribution of measurement outcomes.

### Graphs

1. **Circuit Diagram**: A clear representation of the Shor's Algorithm quantum circuit, highlighting key stages such as:
   - Application of Hadamard gates.
   - Controlled modular exponentiation.
   - Inverse QFT.

   ![Circuit Diagram for N=15 and a=7](examples/shor_circuit.png)

2. **Probability Peaks**: A histogram displaying the probability of measured phases. The red dashed lines indicate expected periodicity based on the algorithm's results. This helps visualize the quantum period-finding process and highlights key phases contributing to factorization. Note that these graphs demonstrate probabilities and are best interpreted with multiple runs to mitigate probabilistic noise.

   ![Probability Peaks for N=15 and a=7](examples/probability_peaks.png)

## Important Notes

- The project simulates Shor's Algorithm using Qiskit's classical simulator backend. The simulator computes the exact, noiseless statevector, so these are the ideal-case results; real quantum hardware would introduce additional gate and decoherence noise, not remove it, so simulator results here are a best-case reference rather than something hardware would improve on.

- Due to the probabilistic nature of quantum algorithms, outputs may vary between runs. For more consistent results, increase the number of shots or run the simulation multiple times.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shidsa6/shors-algorithm-project.git
   cd shors-algorithm-project
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
   python -m unittest tests/test_shor_algorithm.py
   ```

## License

This project is licensed under the terms of the LICENSE file included in the repository.

---

Feel free to reach out with any questions or suggestions for improvements!
