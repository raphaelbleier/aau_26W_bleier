"""Tests zum Initial-Dictionary aus Exercise 4.3."""
import unittest
import numpy as np
from Bleier_sheet_4 import initial_simplex_dictionary, example_data


class DictionaryTests(unittest.TestCase):
    def test_example(self):
        c, A, b, B = example_data()
        d = initial_simplex_dictionary(c, A, b, B)
        self.assertEqual(d['dimension'], (3, 6))
        self.assertEqual(d['B'], [3, 4, 5])
        self.assertEqual(d['N'], [0, 1, 2])
        np.testing.assert_array_equal(d['b_bar'], b)
        np.testing.assert_array_equal(d['A_bar'], A[:, :3])
        np.testing.assert_array_equal(d['c_bar_N'], [-1, 2, 6])
        np.testing.assert_array_equal(d['x'], [0, 0, 0, 10, 8, 6])
        np.testing.assert_array_equal(d['x_N'], [0, 0, 0])
        self.assertEqual(d['z_bar'], 0)
        self.assertTrue(d['is_feasible'])

    def test_general_basis_dictionary_identities(self):
        c, A, b, _ = example_data()
        # Absichtlich andere Reihenfolge und keine Einheitsbasis.
        B = [2, 0, 1]
        d = initial_simplex_dictionary(c, A, b, B)
        self.assertEqual(d['B'], B)
        np.testing.assert_allclose(A @ d['x'], b)
        self.assertAlmostEqual(c @ d['x'], d['z_bar'])
        for xN in (np.zeros(3), np.array([0.1, 0.2, 0.3]), np.array([-2, 1, 4])):
            x = np.zeros(6)
            x[d['N']] = xN
            x[B] = d['b_bar'] - d['A_bar'] @ xN
            np.testing.assert_allclose(A @ x, b, atol=1e-12)
            self.assertAlmostEqual(c @ x, d['z_bar'] + d['c_bar_N'] @ xN)

    def test_infeasible_basis(self):
        d = initial_simplex_dictionary([1, 0], [[1, 1]], [-1], [1])
        self.assertFalse(d['is_feasible'])
        np.testing.assert_array_equal(d['x_B'], [-1])

    def test_degenerate_basis_is_feasible(self):
        d = initial_simplex_dictionary([1, 0], [[1, 1]], [0], [1])
        self.assertTrue(d['is_feasible'])

    def test_no_nonbasic_variables(self):
        d = initial_simplex_dictionary([1, 2], [[1, 0], [0, 1]], [3, 4], [0, 1])
        self.assertEqual(d['A_bar'].shape, (2, 0))
        self.assertEqual(d['c_bar_N'].shape, (0,))
        self.assertEqual(d['z_bar'], 11)

    def test_singular_basis(self):
        with self.assertRaises(np.linalg.LinAlgError):
            initial_simplex_dictionary([1, 2], [[1, 2], [2, 4]], [3, 6], [0, 1])

    def test_invalid_basis(self):
        c, A, b, _ = example_data()
        for B in ([0, 0, 1], [0, 1], [-1, 1, 2], [0, 1, 6], [0, 1, 2.0], [False, 1, 2]):
            with self.subTest(B=B), self.assertRaises(ValueError):
                initial_simplex_dictionary(c, A, b, B)

    def test_invalid_shapes_and_values(self):
        c, A, b, B = example_data()
        for cc, aa, bb in ((c[:2], A, b), (c, A, b[:2]), (c, A.ravel(), b),
                           (c, A, [np.inf, 8, 6]), (c, A, [np.nan, 8, 6])):
            with self.subTest(), self.assertRaises(ValueError):
                initial_simplex_dictionary(cc, aa, bb, B)

    def test_inputs_unchanged(self):
        c, A, b, B = example_data()
        originals = c.copy(), A.copy(), b.copy(), B.copy()
        initial_simplex_dictionary(c, A, b, B)
        for original, current in zip(originals, (c, A, b, B)):
            np.testing.assert_array_equal(original, current)


if __name__ == '__main__':
    unittest.main()
