from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram, circuit_drawer
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
from shor_algorithm import run_shor_algorithm, extract_period, modular_exponentiation

def clean_examples_folder():
    if os.path.exists("examples"):
        shutil.rmtree("examples")
    os.makedirs("examples", exist_ok=True)

def create_display_circuit(N, a):
    n_count = 3
    num_target_qubits = int(np.ceil(np.log2(N)))
    qc = QuantumCircuit(n_count + num_target_qubits, n_count)
    
    for q in range(n_count):
        qc.h(q)
    qc.barrier(label='H⊗n')
    
    qc.cp(2 * np.pi / N, 0, n_count)
    qc.barrier(label='Controlled-Ua')
    
    for i in reversed(range(n_count)):
        qc.h(i)
    qc.barrier(label='QFT†')
    
    qc.measure(range(n_count), range(n_count))
    return qc

def create_shor_circuit(N, a):
    n_count = 20
    num_target_qubits = int(np.ceil(np.log2(N)))
    qc = QuantumCircuit(n_count + num_target_qubits, n_count)
    
    for q in range(n_count):
        qc.h(q)
    qc.barrier()
    
    for i in range(n_count):
        power = 2**i
        for target in range(num_target_qubits):
            factor = pow(a, power, N)
            angle = 2 * np.pi * factor / N
            qc.cp(angle, i, n_count + target)
    qc.barrier()
    
    for i in reversed(range(n_count)):
        for j in range(i):
            qc.cp(-np.pi/2**(i-j), j, i)
        qc.h(i)
    qc.barrier()
    
    qc.measure(range(n_count), range(n_count))
    return qc

def plot_probability_peaks(N, a):
    simulator = Aer.get_backend("qasm_simulator")
    shots = 16384
    
    shor_circuit = create_shor_circuit(N, a)
    result = execute(shor_circuit, backend=simulator, shots=shots).result()
    counts = result.get_counts()
    
    phases = []
    probabilities = []
    n_count = int(np.ceil(np.log2(N))) + 1
    
    sorted_counts = dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))
    total_shots = sum(sorted_counts.values())
    
    for bitstring, count in sorted_counts.items():
        phase = int(bitstring, 2) / (2**len(bitstring))
        phases.append(phase)
        probabilities.append(count/total_shots)
    
    r = extract_period(counts, N)
    
    plt.figure(figsize=(15, 8))
    plt.bar(phases, probabilities, width=0.5/(2**n_count), 
            align='center', alpha=0.6, color='blue',
            label='Measurement Probabilities')
    
    if r is not None:
        period_lines = []
        for k in range(r):
            line = plt.axvline(x=k/r, color='red', linestyle='--', alpha=0.7)
            if k == 0:
                period_lines.append(line)
            plt.text(k/r, max(probabilities), f'{k}/{r}', 
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
    plt.show()

clean_examples_folder()

N = 15
a = 7
display_circuit = create_display_circuit(N, a)
circuit_path = "examples/shor_circuit.png"
circuit_drawer(display_circuit, output="mpl", scale=1.2, style={'name': 'bw'})\
    .savefig(circuit_path)
print(f"Circuit diagram saved to {circuit_path}")

plot_probability_peaks(N, a)
