from qiskit import QuantumCircuit, Aer, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from math import gcd
import numpy as np

def modular_exponentiation(base, exp, mod):
    """Compute (base^exp) % mod efficiently."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result

def quantum_fourier_transform(n):
    """Create QFT circuit."""
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.h(i)
        for j in range(i+1, n):
            qc.cp(2*np.pi/2**(j-i+1), i, j)
    return qc

def run_shor_algorithm(N, a):
    """Run Shor's algorithm."""
    if gcd(a, N) != 1:
        return gcd(a, N), N // gcd(a, N)

    # Create quantum circuit
    n_count = 8  # Number of counting qubits
    num_target_qubits = int(np.ceil(np.log2(N)))
    
    qc = QuantumCircuit(n_count + num_target_qubits, n_count)
    
    # Initialize counting qubits
    for q in range(n_count):
        qc.h(q)
    qc.barrier()
    
    # Controlled modular multiplication
    for i in range(n_count):
        power = 2**i
        for target in range(num_target_qubits):
            factor = pow(a, power, N)
            angle = 2 * np.pi * factor / N
            qc.cp(angle, i, n_count + target)
    qc.barrier()
    
    # Inverse QFT
    for i in reversed(range(n_count)):
        for j in range(i):
            qc.cp(-np.pi/2**(i-j), j, i)
        qc.h(i)
    qc.barrier()
    
    # Measure
    qc.measure(range(n_count), range(n_count))
    
    # Execute
    simulator = Aer.get_backend('aer_simulator')
    job = simulator.run(transpile(qc, simulator), shots=1024)
    counts = job.result().get_counts()
    
        # Extract period - Updated to pass 'a'
    r = extract_period(counts, N, a)
    if not r:
        return None, None
        
    if r % 2 != 0:
        return None, None
        
    factor1 = gcd(modular_exponentiation(a, r//2, N) - 1, N)
    factor2 = gcd(modular_exponentiation(a, r//2, N) + 1, N)
    
    if factor1 * factor2 != N:
        return None, None
        
    return factor1, factor2

def extract_period(counts, N, a):
    """Extract period r where a^r ≡ 1 (mod N)"""
    # First find quantum measurement differences
    measured_values = [int(key, 2) for key in counts.keys()]
    measured_values.sort()
    
    # Calculate possible periods from measurements
    periods = []
    for i in range(1, len(measured_values)):
        r = measured_values[i] - measured_values[i-1]
        if r > 0:
            periods.append(r)
    
    # Verify each candidate period
    for r in periods:
        if modular_exponentiation(a, r, N) == 1:
            return r
            
    # Direct period calculation if measurement fails
    for r in range(1, N):
        if modular_exponentiation(a, r, N) == 1:
            return r
            
    return None

if __name__ == "__main__":
    N = 15
    a = 7
    factors = run_shor_algorithm(N, a)
    if factors and factors[0] and factors[1]:
        print(f"Factors of {N} are: {factors[0]} and {factors[1]}")
    else:
        print("Failed to find factors. Try again.")