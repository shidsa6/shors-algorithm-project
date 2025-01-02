import unittest
from shor_algorithm import run_shor_algorithm

class TestShorsAlgorithm(unittest.TestCase):
    def test_shor_algorithm(self):
        N = 15  # Number to factor
        a = 7   # Random base
        factor1, factor2 = run_shor_algorithm(N, a)
        self.assertTrue(factor1 * factor2 == N)

    def test_invalid_base(self):
        N = 15
        a = 1  # Invalid base (gcd(a, N) != 1)
        factor1, factor2 = run_shor_algorithm(N, a)
        self.assertIsNone(factor1)
        self.assertIsNone(factor2)

if __name__ == "__main__":
    unittest.main()
