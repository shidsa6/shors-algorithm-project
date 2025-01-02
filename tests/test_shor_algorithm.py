import unittest
import sys
import os
# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shor_algorithm import run_shor_algorithm

class TestShorsAlgorithm(unittest.TestCase):
    def test_shor_algorithm(self):
        """
        Verify that Shor's Algorithm correctly factors a given number N.

        Specifically, ensure that the product of the computed factors equals N.
        """
        N = 15  # Number to factor
        a = 7   # Random base
        factor1, factor2 = run_shor_algorithm(N, a)
        self.assertTrue(factor1 * factor2 == N)

    def test_invalid_base(self):
        """
        Verify that Shor's Algorithm correctly handles invalid bases.

        Specifically, ensure that invalid bases (where gcd(a, N) != 1) result in None.
        """
        N = 15
        a = 1  # Invalid base (gcd(a, N) != 1)
        factor1, factor2 = run_shor_algorithm(N, a)
        self.assertIsNone(factor1)
        self.assertIsNone(factor2)

if __name__ == "__main__":
    unittest.main()
