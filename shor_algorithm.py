"""Shor's algorithm for integer factorization.

Implements the full quantum period-finding subroutine (controlled modular
exponentiation + inverse QFT + continued-fraction period extraction), not
just a classical fallback dressed up as a quantum circuit.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from math import gcd
from fractions import Fraction
import numpy as np


def modular_exponentiation(base, exp, mod):
    """Compute (base^exp) % mod efficiently (classical, square-and-multiply)."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result


def quantum_fourier_transform(n):
    """Create an n-qubit QFT circuit (standard construction, includes the
    final swap network so it matches the textbook/qiskit.circuit.library.QFT
    convention)."""
    qc = QuantumCircuit(n, name="QFT")
    for i in range(n):
        qc.h(i)
        for j in range(i + 1, n):
            qc.cp(2 * np.pi / 2 ** (j - i + 1), i, j)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)
    return qc


def inverse_qft(n):
    """Exact inverse of quantum_fourier_transform(n).

    Built via QuantumCircuit.inverse() rather than a hand-written gate
    sequence: a hand-rolled "inverse QFT" is easy to get subtly wrong (wrong
    control/target qubit on the controlled-phase gates), and a wrong inverse
    QFT silently destroys quantum phase estimation without raising any
    error - the circuit just produces noise that happens to look like
    plausible measurement data. Deriving it mechanically from the (simple,
    directly-checkable) forward QFT above avoids re-introducing that bug.
    """
    return quantum_fourier_transform(n).inverse()


def _modmul_matrix(a, N, n_target):
    """Permutation matrix for |y> -> |a*y mod N> (y < N), identity on y >= N.

    Multiplication by a is invertible mod N (since gcd(a, N) == 1 is
    required by the caller), so this is a genuine permutation of the basis
    states 0..N-1, and therefore a valid unitary once padded out to the
    full 2^n_target-dimensional space (padding with the identity on the
    unused states y >= N keeps it unitary).
    """
    dim = 2 ** n_target
    U = np.zeros((dim, dim))
    for y in range(dim):
        if y < N:
            U[(a * y) % N, y] = 1.0
        else:
            U[y, y] = 1.0
    return U


def controlled_modmul_gate(a, N, n_target):
    """Controlled-U_a gate where U_a|y> = |a*y mod N> for y < N.

    Built as an explicit dense unitary (feasible for the small N used in a
    teaching/demo implementation like this one - target register has
    2^n_target <= a few dozen basis states). This is mathematically exact,
    not an approximation: for genuine controlled modular *exponentiation*,
    U_a applied 2^i times equals U_{a^(2^i) mod N} applied once, because
    iterated multiplication mod N is associative. So building
    controlled_modmul_gate(pow(a, 2**i, N), N, n_target) for each counting
    qubit i is exactly equivalent to (and much simpler than) synthesizing
    2^i repetitions of a controlled-multiply-by-a circuit.
    """
    U = _modmul_matrix(a, N, n_target)
    qc = QuantumCircuit(n_target, name=f"x{a}mod{N}")
    qc.unitary(U, range(n_target))
    return qc.to_gate().control(1)


def build_shor_circuit(N, a, n_count):
    """Build the full QPE-based order-finding circuit for a mod N."""
    n_target = int(np.ceil(np.log2(N)))
    counting = QuantumRegister(n_count, "count")
    target = QuantumRegister(n_target, "target")
    creg = ClassicalRegister(n_count, "c")
    qc = QuantumCircuit(counting, target, creg)

    # Counting register: uniform superposition.
    qc.h(counting)
    # Target register: prepare |1> (the multiplicative identity mod N).
    qc.x(target[0])
    qc.barrier()

    # Controlled modular exponentiation: for counting qubit i, apply
    # controlled-U_{a^(2^i) mod N} onto the target register.
    for i in range(n_count):
        power_a = pow(a, 2 ** i, N)
        gate = controlled_modmul_gate(power_a, N, n_target)
        qc.append(gate, [counting[i]] + list(target))
    qc.barrier()

    # Inverse QFT on the counting register, then measure.
    qc.append(inverse_qft(n_count).to_gate(label="QFT†"), counting)
    qc.barrier()
    qc.measure(counting, creg)

    return qc


def extract_period(counts, N, a, n_count):
    """Extract the order r of a mod N from QPE measurement outcomes.

    Standard continued-fraction procedure (Nielsen & Chuang Sec. 5.3.1):
    each measured integer m encodes a phase estimate m / 2^n_count ~ k/r
    for some integer k. Expanding that phase as a continued fraction and
    taking convergents' denominators gives candidate periods r, which are
    then verified classically (a^r mod N == 1). Falls back to nothing
    (returns None) if no measured outcome yields a valid period - this is
    a probabilistic algorithm, so callers should be prepared to retry with
    fresh shots, not treat a single None as "no period exists".
    """
    candidates = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    for bitstring, _ in candidates:
        measured = int(bitstring, 2)
        if measured == 0:
            continue
        phase = measured / (2 ** n_count)
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        if r == 0:
            continue
        if modular_exponentiation(a, r, N) == 1:
            return r
        # The continued-fraction denominator can be a proper divisor of the
        # true period (happens when gcd(k, r) > 1 for the measured k) - try
        # small multiples before giving up on this candidate.
        for mult in range(2, 5):
            if modular_exponentiation(a, r * mult, N) == 1:
                return r * mult
    return None


def run_shor_algorithm(N, a, n_count=None, shots=4096, max_attempts=5):
    """Run Shor's algorithm to factor N using base a.

    Returns (factor1, factor2) with factor1 * factor2 == N, or (None, None)
    if factoring failed (e.g. an unlucky choice of a, or the period-finding
    subroutine not converging within max_attempts - both are expected,
    normal outcomes of a probabilistic algorithm, not bugs).
    """
    if N < 2:
        raise ValueError("N must be >= 2")
    common = gcd(a, N)
    if common != 1:
        # a shares a factor with N already - no quantum step needed.
        return common, N // common

    n_target = int(np.ceil(np.log2(N)))
    if n_count is None:
        # Nielsen & Chuang: need 2^n_count > N^2 for a high-confidence
        # single-shot success probability; use 2*n_target+3 bits of
        # precision as a safe margin above that bound.
        n_count = max(8, 2 * n_target + 3)

    simulator = AerSimulator()

    for attempt in range(max_attempts):
        qc = build_shor_circuit(N, a, n_count)
        job = simulator.run(transpile(qc, simulator), shots=shots)
        counts = job.result().get_counts()

        r = extract_period(counts, N, a, n_count)
        if r is None:
            continue
        if r % 2 != 0:
            continue

        half = modular_exponentiation(a, r // 2, N)
        if half == N - 1:
            # a^(r/2) = -1 mod N: this run is uninformative, the gcd trick
            # below would only yield the trivial factors {1, N}. Retry.
            continue

        factor1 = gcd(half - 1, N)
        factor2 = gcd(half + 1, N)

        if factor1 * factor2 == N and 1 < factor1 < N and 1 < factor2 < N:
            return factor1, factor2

    return None, None


def factor_number(N, max_a_attempts=10, **kwargs):
    """Factor N end-to-end, picking random bases automatically.

    run_shor_algorithm(N, a) can fail for a fixed a even with a perfectly
    correct quantum implementation - some choices of a have odd order, or
    satisfy a^(r/2) = -1 mod N, and Shor's algorithm is provably unable to
    extract factors from those (this is a property of the math, not a bug).
    The textbook fix is simply to retry with a freshly-random a: for random
    a coprime to N, the algorithm succeeds with probability >= 1/2, so a
    handful of attempts drives failure probability down exponentially.
    """
    import random

    if N < 2:
        raise ValueError("N must be >= 2")
    if N % 2 == 0:
        return 2, N // 2

    tried = set()
    for _ in range(max_a_attempts):
        a = random.randint(2, N - 1)
        if a in tried:
            continue
        tried.add(a)
        if gcd(a, N) != 1:
            return gcd(a, N), N // gcd(a, N)
        factors = run_shor_algorithm(N, a, **kwargs)
        if factors != (None, None):
            return factors
    return None, None


if __name__ == "__main__":
    N = 15
    a = 7
    factors = run_shor_algorithm(N, a)
    if factors and factors[0] and factors[1]:
        print(f"Factors of {N} are: {factors[0]} and {factors[1]}")
    else:
        print("Failed to find factors. Try again.")
