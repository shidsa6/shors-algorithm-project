from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram, circuit_drawer
from qiskit_aer import AerSimulator
from qiskit import transpile
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
from shor_algorithm import build_shor_circuit, extract_period

def clean_examples_folder():
    if os.path.exists("examples"):
        shutil.rmtree("examples")
    os.makedirs("examples", exist_ok=True)

def create_display_circuit(N, a, n_count=3):
    """A small, readable version of the real circuit (few counting qubits)
    purely for the circuit diagram - uses the same building blocks as the
    actual algorithm in shor_algorithm.py, just with n_count kept small so
    the drawing stays legible.
    """
    return build_shor_circuit(N, a, n_count)

def plot_probability_peaks(N, a, n_count=8, shots=16384):
    """
    Creates a histogram of the probability distribution of Shor's algorithm
    measurement outcomes for the given N and a, using the real quantum
    circuit from shor_algorithm.py (controlled modular exponentiation +
    inverse QFT). The x-axis is the measured phase m/2^n_count; the red
    dashed lines mark the phases k/r predicted by the period r that
    extract_period recovers from these same measurements.
    """
    simulator = AerSimulator()

    shor_circuit = build_shor_circuit(N, a, n_count)
    result = simulator.run(transpile(shor_circuit, simulator), shots=shots).result()
    counts = result.get_counts()

    phases = []
    probabilities = []

    sorted_counts = dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))
    total_shots = sum(sorted_counts.values())

    for bitstring, count in sorted_counts.items():
        phase = int(bitstring, 2) / (2 ** n_count)
        phases.append(phase)
        probabilities.append(count / total_shots)

    r = extract_period(counts, N, a, n_count)

    plt.figure(figsize=(15, 8))
    plt.bar(phases, probabilities, width=0.5 / (2 ** n_count),
            align='center', alpha=0.6, color='blue',
            label='Measurement Probabilities')

    if r is not None:
        period_lines = []
        for k in range(r):
            line = plt.axvline(x=k / r, color='red', linestyle='--', alpha=0.7)
            if k == 0:
                period_lines.append(line)
            plt.text(k / r, max(probabilities), f'{k}/{r}',
                    rotation=90, va='bottom')
        if period_lines:
            period_lines[0].set_label('Period Markers')

    plt.xlabel("Phase")
    plt.ylabel("Probability")
    plt.title(f"Quantum Period Finding (N={N}, a={a}, Period={r if r else 'Not Found'})")
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right')
    plt.xlim(-0.05, 1.05)
    plt.ylim(0, max(probabilities) * 1.2)

    plt.savefig("examples/probability_peaks.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    clean_examples_folder()

    N = 15
    a = 7
    display_circuit = create_display_circuit(N, a)
    circuit_path = "examples/shor_circuit.png"
    circuit_drawer(display_circuit, output="mpl", scale=1.2, style={'name': 'bw'}) \
        .savefig(circuit_path)
    print(f"Circuit diagram saved to {circuit_path}")

    plot_probability_peaks(N, a)
    print("Probability peaks saved to examples/probability_peaks.png")
