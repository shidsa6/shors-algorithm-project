import unittest
import sys
import os
import numpy as np
from math import gcd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shor_algorithm import (
    run_shor_algorithm,
    factor_number,
    modular_exponentiation,
    quantum_fourier_transform,
    inverse_qft,
    controlled_modmul_gate,
    extract_period,
)


class TestModularExponentiation(unittest.TestCase):
    def test_matches_python_pow(self):
        for base, exp, mod in [(7, 4, 15), (2, 10, 21), (5, 0, 13), (3, 7, 35)]:
            self.assertEqual(modular_exponentiation(base, exp, mod), pow(base, exp, mod))


class TestInverseQFT(unittest.TestCase):
    """Regression guard: a hand-rolled inverse QFT is easy to get subtly
    wrong (this project previously shipped one that was NOT actually the
    inverse of its own forward QFT, which silently broke period-finding
    without raising any error). Check the actual linear-algebra identity
    instead of trusting the code to "look right".
    """

    def test_is_true_inverse_of_forward_qft(self):
        from qiskit.quantum_info import Operator

        for n in [2, 3, 4, 5]:
            qft_op = Operator(quantum_fourier_transform(n))
            inv_op = Operator(inverse_qft(n))
            product = qft_op.compose(inv_op)
            self.assertTrue(
                np.allclose(product.data, np.eye(2 ** n), atol=1e-8),
                f"QFT composed with inverse_qft is not the identity for n={n}",
            )


class TestControlledModularMultiplication(unittest.TestCase):
    """Regression guard: the controlled modular exponentiation step
    previously did nothing at all (the target register was never touched,
    so it stayed |0...0> with probability ~1 regardless of a, N, or which
    counting qubit fired). Check the actual permutation the gate performs.
    """

    def test_control_off_is_identity(self):
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        N, a, n_target = 15, 7, 4
        gate = controlled_modmul_gate(a, N, n_target)
        for y in range(N):
            qc = QuantumCircuit(1 + n_target)
            for b in range(n_target):
                if (y >> b) & 1:
                    qc.x(1 + b)
            qc.append(gate, range(1 + n_target))
            probs = Statevector.from_instruction(qc).probabilities_dict()
            state, prob = max(probs.items(), key=lambda kv: kv[1])
            self.assertAlmostEqual(prob, 1.0, places=6)
            self.assertEqual(int(state[-1]), 0, "control qubit should read 0")
            self.assertEqual(int(state[:-1], 2), y, "target should be unchanged when control=0")

    def test_control_on_multiplies_mod_n(self):
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        N, a, n_target = 15, 7, 4
        gate = controlled_modmul_gate(a, N, n_target)
        for y in range(N):
            qc = QuantumCircuit(1 + n_target)
            qc.x(0)  # control on
            for b in range(n_target):
                if (y >> b) & 1:
                    qc.x(1 + b)
            qc.append(gate, range(1 + n_target))
            probs = Statevector.from_instruction(qc).probabilities_dict()
            state, prob = max(probs.items(), key=lambda kv: kv[1])
            self.assertAlmostEqual(prob, 1.0, places=6)
            self.assertEqual(int(state[-1]), 1, "control qubit should read 1")
            self.assertEqual(int(state[:-1], 2), (a * y) % N,
                            f"expected a*y mod N = {(a*y)%N} for y={y}")


class TestExtractPeriod(unittest.TestCase):
    def test_recovers_known_period_from_clean_qpe_peaks(self):
        # For N=15, a=7 the true order is 4. Ideal QPE measurements cluster
        # at m/2^n_count = k/4 for k=0..3.
        n_count = 8
        counts = {
            format(0, '08b'): 100,
            format(64, '08b'): 300,
            format(128, '08b'): 300,
            format(192, '08b'): 300,
        }
        self.assertEqual(extract_period(counts, 15, 7, n_count), 4)

    def test_returns_none_on_uninformative_data(self):
        n_count = 8
        counts = {format(1, '08b'): 1}  # phase ~ 1/256, no valid small period
        # Should not crash, and should not fabricate a period out of noise.
        r = extract_period(counts, 15, 7, n_count)
        if r is not None:
            self.assertEqual(modular_exponentiation(7, r, 15), 1)


class TestShorsAlgorithm(unittest.TestCase):
    def test_shor_algorithm_known_case(self):
        """N=15, a=7 is a reliable case (order 4, a^2 != -1 mod N)."""
        factor1, factor2 = run_shor_algorithm(15, 7)
        self.assertIsNotNone(factor1)
        self.assertIsNotNone(factor2)
        self.assertEqual(factor1 * factor2, 15)
        self.assertTrue(1 < factor1 < 15)
        self.assertTrue(1 < factor2 < 15)

    def test_invalid_base(self):
        """gcd(a, N) != 1 should short-circuit to the shared factor, not fail."""
        factor1, factor2 = run_shor_algorithm(15, 3)  # gcd(3, 15) = 3
        self.assertEqual(factor1, 3)
        self.assertEqual(factor2, 5)

    def test_a_equals_one_is_meaningless_and_handled(self):
        # gcd(1, N) == 1, so this goes through the quantum path, which
        # cannot extract a period from a=1 (order 1, odd) - should fail
        # honestly rather than return a wrong answer.
        factor1, factor2 = run_shor_algorithm(15, 1, max_attempts=2)
        self.assertIsNone(factor1)
        self.assertIsNone(factor2)

    def test_factor_number_end_to_end(self):
        """factor_number automatically retries with random bases and should
        reliably factor small N."""
        for N in [15, 21]:
            f1, f2 = factor_number(N, max_a_attempts=10)
            self.assertIsNotNone(f1, f"failed to factor {N}")
            self.assertEqual(f1 * f2, N)
            self.assertTrue(1 < f1 < N)
            self.assertTrue(1 < f2 < N)


if __name__ == "__main__":
    unittest.main()
