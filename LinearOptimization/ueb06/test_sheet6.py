"""Tests für Exercise 6.3: Simplex-Algorithmus auf Example 2.2."""
import numpy as np
import pytest

from Bleier_sheet_6 import (
    choose_entering_variable_index,
    choose_leaving_variable_index,
    create_simplex_dictionary,
    example_data,
    solve_simplex,
)


def test_initial_dictionary_matches_sheet5():
    """Das umbenannte create_simplex_dictionary liefert die Zahlen vom Blatt 5."""
    c, A, b, B = example_data()
    d = create_simplex_dictionary(c, A, b, B)
    assert d["B"] == [3, 4, 5]
    assert d["N"] == [0, 1, 2]
    assert np.allclose(d["b_bar"], [10, 8, 6])
    assert np.allclose(d["c_bar_N"], [-1, 2, 6])
    assert d["z_bar"] == 0
    assert d["is_feasible"]


def test_first_pivot_matches_hand_computation():
    """x3 tritt ein (Kosten 6), Quotienten 8/2=4 und 6/1=6 -> x5 (Index 4) tritt aus."""
    c, A, b, B = example_data()
    d = create_simplex_dictionary(c, A, b, B)
    entering = choose_entering_variable_index(d)
    assert entering == 2
    leaving = choose_leaving_variable_index(d, entering)
    assert leaving == 4


def test_simplex_solves_example_2_2():
    """Optimum von Example 2.2: z = 26 bei (x1, x2, x3) = (0, 1, 4)."""
    c, A, b, B = example_data()
    d, iterations = solve_simplex(c, A, b, B)
    assert d["z_bar"] == pytest.approx(26.0)
    assert np.allclose(d["x"], [0, 1, 4, 7, 0, 0])
    assert all(rc <= 1e-9 for rc in np.ravel(d["c_bar_N"]))
    assert iterations == 2


def test_simplex_from_optimal_basis_terminates_immediately():
    """Startet man schon optimal, gibt es keinen Eintrittskandidaten."""
    c, A, b, _ = example_data()
    d, iterations = solve_simplex(c, A, b, [3, 2, 1])
    assert d["z_bar"] == pytest.approx(26.0)
    assert iterations == 0


def test_simplex_detects_unbounded():
    """max x1 mit x1 - x2 + x3 = 1: nach einem Pivot bleibt die Spalte von x2
    negativ -> unbeschränkt."""
    c = np.array([1.0, 0.0, 0.0])
    A = np.array([[1.0, -1.0, 1.0]])
    b = np.array([1.0])
    with pytest.raises(RuntimeError, match="unbeschränkt"):
        solve_simplex(c, A, b, [2])


def test_simplex_rejects_infeasible_start():
    """Ein Start mit negativem b_bar ist keine zulässige Basislösung."""
    c, A, b, _ = example_data()
    with pytest.raises(ValueError, match="zulässig"):
        solve_simplex(c, A, b, [0, 1, 2])


def test_pivot_updates_basis_in_place_order():
    """Der austretende Index wird an seiner Position ersetzt, nicht umsortiert."""
    c, A, b, B = example_data()
    d = create_simplex_dictionary(c, A, b, B)
    B_new = list(d["B"])
    B_new[B_new.index(4)] = 2
    assert B_new == [3, 2, 5]
    d2 = create_simplex_dictionary(c, A, b, B_new)
    assert d2["B"] == [3, 2, 5]
    # Zwischenlösung (0, 0, 4): z = 24
    assert d2["z_bar"] == pytest.approx(24.0)
