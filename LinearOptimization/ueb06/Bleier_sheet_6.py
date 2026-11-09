"""Simplex-Algorithmus komplett: Dictionary erstellen, Pivot wählen, iterieren. Exercise 6.3.

create_simplex_dictionary ist die umbenannte initial_simplex_dictionary vom Blatt 4.
Wie in Exercise 6.1 gezeigt, ist das Neuaufstellen des Dictionaries aus Ax = b
äquivalent zum Umformen im alten Dictionary -- deshalb genügt eine Funktion.
"""
import numpy as np


def create_simplex_dictionary(c, A, b, B):
    """Berechnet x_B = b_bar - A_bar @ x_N; B enthält nullbasierte Indizes.

    Die Reihenfolge von B bleibt erhalten. N wird aufsteigend sortiert.
    Singuläre Basen führen zu numpy.linalg.LinAlgError.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    if A.ndim != 2:
        raise ValueError("A muss eine zweidimensionale Matrix sein")
    m, n = A.shape
    if m == 0 or n < m or b.shape != (m,) or c.shape != (n,):
        raise ValueError("Dimensionen von A, b und c passen nicht zusammen")
    if not all(np.all(np.isfinite(v)) for v in (A, b, c)):
        raise ValueError("Alle Koeffizienten müssen endlich sein")
    B = list(B)
    if (len(B) != m or len(set(B)) != m
            or any(isinstance(i, (bool, np.bool_))
                   or not isinstance(i, (int, np.integer))
                   or not 0 <= i < n for i in B)):
        raise ValueError("B muss m verschiedene gültige Spaltenindizes enthalten")
    B = [int(i) for i in B]
    N = sorted(set(range(n)) - set(B))
    A_B = A[:, B]
    A_N = A[:, N]
    c_B = c[B]
    c_N = c[N]

    # Lösen statt Invertieren liefert dieselben Größen ohne explizite Inverse.
    b_bar = np.linalg.solve(A_B, b)
    A_bar = np.linalg.solve(A_B, A_N)
    z_bar = float(c_B @ b_bar)
    c_bar_N = c_N - c_B @ A_bar
    x_B = b_bar.copy()
    x_N = np.zeros(len(N))
    x = np.zeros(n)
    x[B] = x_B
    is_feasible = bool(np.all(b_bar >= 0))
    return {
        "dimension": (m, n), "B": B, "N": N,
        "b_bar": b_bar, "A_bar": A_bar,
        "z_bar": z_bar, "c_bar_N": c_bar_N,
        "x_B": x_B, "x_N": x_N, "x": x,
        "is_feasible": is_feasible,
    }


def choose_entering_variable_index(simplex_dict):
    """
    Chooses the index of the entering variable for the simplex method based on the most positive reduced cost.

    Parameters:
    - simplex_dict (dict): A dictionary containing the simplex dictionary components.

    Returns:
    - int or None: The index of the entering variable, or None if optimal.
    """
    c_bar_N = np.ravel(np.asarray(simplex_dict["c_bar_N"], dtype=float))
    N = [int(i) for i in simplex_dict["N"]]
    if c_bar_N.shape != (len(N),):
        raise ValueError("c_bar_N und N müssen gleich lang sein")

    # Check if all reduced costs are non-positive (tolerance for numerical stability)
    if not np.any(c_bar_N > 1e-9):
        return None  # Optimal solution reached; no entering variable

    # Choose the nonbasic variable with the maximum positive reduced cost.
    # np.argmax keeps the first index, so a tie goes to the earlier entry of N.
    max_idx = int(np.argmax(c_bar_N))

    # Select the correct index in N
    entering_var_ind = N[max_idx]

    return entering_var_ind


def choose_leaving_variable_index(simplex_dict, entering_var_ind):
    """
    Chooses the index of the leaving variable for the simplex method using the minimum-ratio test.

    Parameters:
    - simplex_dict (dict): A dictionary containing the simplex dictionary components.
    - entering_var_ind (int): The original index of the entering variable.

    Returns:
    - int or None: The original index of the leaving variable, or None if unbounded.
    """
    b_bar = np.ravel(np.asarray(simplex_dict["b_bar"], dtype=float))
    A_bar = np.asarray(simplex_dict["A_bar"], dtype=float)
    N = [int(i) for i in simplex_dict["N"]]
    B = [int(i) for i in simplex_dict["B"]]
    if A_bar.ndim != 2 or A_bar.shape != (len(B), len(N)) or b_bar.shape != (len(B),):
        raise ValueError("A_bar, b_bar, B und N passen nicht zusammen")
    entering_var_ind = int(entering_var_ind)

    # Find the index of the entering variable among the nonbasis variables
    j_idx = N.index(entering_var_ind)

    # Extract the column corresponding to the entering variable from A_bar
    entering_col = A_bar[:, j_idx]

    # Minimum-ratio test: Consider only rows with strictly positive coefficients
    # (using a tolerance for numerical stability)
    valid_rows = np.where(entering_col > 1e-9)[0]

    # If no positive entries exist, the problem is unbounded
    if len(valid_rows) == 0:
        return None

    # Compute the ratios (b_bar / entering_col) for the valid rows
    ratios = b_bar[valid_rows] / entering_col[valid_rows]

    # Find the row index that yields the minimum ratio.
    # np.argmin keeps the first row, so a tie follows the current order of B.
    min_ratio_idx = int(np.argmin(ratios))
    row_idx = int(valid_rows[min_ratio_idx])

    # Select the correct index in B
    leaving_var_ind = B[row_idx]

    return leaving_var_ind


def solve_simplex(c, A, b, B, max_iterations=100):
    """Simplex-Algorithmus: startet bei der Basis B und pivoted, bis alle
    reduzierten Kosten nichtpositiv sind (Abbruchkriterium laut Blatt).

    Liefert (dictionary, iterations). Bei positiven reduzierten Kosten ohne
    positive Spalteneinträge ist das Problem unbeschränkt -> RuntimeError.
    Ein nichtzulässiger Start (b_bar < 0) wird vorher abgefangen; Phase 1
    braucht das Blatt hier nicht, Example 2.2 startet zulässig.
    """
    dictionary = create_simplex_dictionary(c, A, b, B)
    if not dictionary["is_feasible"]:
        raise ValueError("Startbasis ist nicht zulässig (b_bar < 0)")
    for iteration in range(1, max_iterations + 1):
        entering = choose_entering_variable_index(dictionary)
        if entering is None:
            # Alle reduzierten Kosten <= 0: optimum erreicht
            return dictionary, iteration - 1
        leaving = choose_leaving_variable_index(dictionary, entering)
        if leaving is None:
            raise RuntimeError(
                f"Problem ist unbeschränkt: Spalte von x{entering + 1} hat keinen positiven Eintrag"
            )
        # Basis tauschen: austretenden Index an seiner Position ersetzen,
        # dann das Dictionary frisch aus Ax = b aufstellen (Exercise 6.1).
        B = list(dictionary["B"])
        B[B.index(leaving)] = entering
        dictionary = create_simplex_dictionary(c, A, b, B)
    raise RuntimeError(f"Keine Konvergenz nach {max_iterations} Iterationen")


def example_data():
    """Example 2.2, nullbasierte Schlupfbasis (4, 5, 6) -> [3, 4, 5]."""
    c = np.array([-1, 2, 6, 0, 0, 0], dtype=float)
    A = np.array([[2, 3, 0, 1, 0, 0],
                  [1, 0, 2, 0, 1, 0],
                  [1, 2, 1, 0, 0, 1]], dtype=float)
    b = np.array([10, 8, 6], dtype=float)
    return c, A, b, [3, 4, 5]


if __name__ == "__main__":
    c, A, b, B = example_data()
    dictionary, iterations = solve_simplex(c, A, b, B)
    print("Example 2.2, solved with the simplex algorithm")
    print(f"iterations: {iterations}")
    print(f"optimal basis B: {dictionary['B']} (1-based: {[i + 1 for i in dictionary['B']]})")
    print(f"objective z: {dictionary['z_bar']}")
    print(f"nonbasic variables: {dictionary['N']} set to 0")
    print(f"solution x: {dictionary['x']}")
