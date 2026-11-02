"""Tests für Entering- und Leaving-Wahl, Exercise 5.3."""
import unittest
import numpy as np
from Bleier_sheet_5 import (
    choose_entering_variable_index,
    choose_leaving_variable_index,
    example_data,
    initial_simplex_dictionary,
)


def pivot(dictionary, entering, leaving):
    """Ein Pivot, nur für die Gegenprobe. Nicht Teil der Abgabe."""
    B = list(dictionary["B"])
    N = list(dictionary["N"])
    row = B.index(leaving)
    col = N.index(entering)
    A = np.array(dictionary["A_bar"], dtype=float)
    b = np.array(dictionary["b_bar"], dtype=float)
    c = np.array(dictionary["c_bar_N"], dtype=float)
    z = float(dictionary["z_bar"])
    pivot_val = A[row, col]
    step = b[row] / pivot_val
    new_b = b - A[:, col] * step
    new_A = A - np.outer(A[:, col], A[row, :]) / pivot_val
    new_b[row] = step
    new_A[row, :] = A[row, :] / pivot_val
    new_A[:, col] = -A[:, col] / pivot_val
    new_A[row, col] = 1.0 / pivot_val
    new_c = c - c[col] * A[row, :] / pivot_val
    new_c[col] = -c[col] / pivot_val
    new_z = z + c[col] * step
    B[row] = entering
    N[col] = leaving
    return {
        "B": B, "N": N, "b_bar": new_b, "A_bar": new_A,
        "c_bar_N": new_c, "z_bar": new_z,
    }


class ChoiceTests(unittest.TestCase):
    def test_example_22_matches_lecture_pivot(self):
        dictionary = initial_simplex_dictionary(*example_data())
        entering = choose_entering_variable_index(dictionary)
        leaving = choose_leaving_variable_index(dictionary, entering)
        self.assertEqual(entering, 2)
        self.assertEqual(leaving, 4)
        updated = pivot(dictionary, entering, leaving)
        np.testing.assert_allclose(updated["b_bar"][updated["B"].index(2)], 4)
        self.assertAlmostEqual(updated["z_bar"], 24)

        # Zweiter Schritt aus Lecture 4: x2 rein, x6 raus, z = 26.
        entering = choose_entering_variable_index(updated)
        leaving = choose_leaving_variable_index(updated, entering)
        self.assertEqual(entering, 1)
        self.assertEqual(leaving, 5)
        updated = pivot(updated, entering, leaving)
        self.assertAlmostEqual(updated["z_bar"], 26)
        self.assertIsNone(choose_entering_variable_index(updated))
        x = np.zeros(6)
        x[updated["B"]] = updated["b_bar"]
        np.testing.assert_allclose(x, [0, 1, 4, 7, 0, 0])

    def test_optimal_and_unbounded(self):
        optimal = {"c_bar_N": np.array([0.0, -2.0]), "N": [0, 1]}
        self.assertIsNone(choose_entering_variable_index(optimal))
        unbounded = {
            "b_bar": np.array([3.0, 4.0]),
            "A_bar": np.array([[-1.0], [0.0]]),
            "N": [1], "B": [0, 2],
        }
        self.assertIsNone(choose_leaving_variable_index(unbounded, 1))

    def test_ties_follow_current_order(self):
        tied = {"c_bar_N": np.array([1.0, 1.0, 0.4]), "N": [4, 1, 2]}
        self.assertEqual(choose_entering_variable_index(tied), 4)
        ratios = {
            "b_bar": np.array([2.0, 2.0]),
            "A_bar": np.array([[1.0], [1.0]]),
            "N": [0], "B": [7, 3],
        }
        self.assertEqual(choose_leaving_variable_index(ratios, 0), 7)

    def test_tolerance_and_input_unchanged(self):
        tiny = {"c_bar_N": np.array([1e-12, -1.0]), "N": [3, 4]}
        self.assertIsNone(choose_entering_variable_index(tiny))
        visible = {"c_bar_N": np.array([1e-8, -1.0]), "N": [3, 4]}
        self.assertEqual(choose_entering_variable_index(visible), 3)
        dictionary = {
            "b_bar": np.array([1.0, 5.0]),
            "A_bar": np.array([[1e-12, 2.0], [1.0, -3.0]]),
            "N": [1, 2], "B": [0, 3],
        }
        before = dictionary["A_bar"].copy()
        self.assertEqual(choose_leaving_variable_index(dictionary, 1), 3)
        np.testing.assert_array_equal(dictionary["A_bar"], before)
        with self.assertRaises(ValueError):
            choose_leaving_variable_index(dictionary, 9)


if __name__ == "__main__":
    unittest.main()
