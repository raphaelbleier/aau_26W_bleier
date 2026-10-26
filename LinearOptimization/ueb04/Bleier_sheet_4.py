"""Initiales Simplex-Dictionary für Exercise 4.3."""
import numpy as np


def initial_simplex_dictionary(c, A, b, B):
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


def example_data():
    c = np.array([-1, 2, 6, 0, 0, 0], dtype=float)
    A = np.array([[2, 3, 0, 1, 0, 0],
                  [1, 0, 2, 0, 1, 0],
                  [1, 2, 1, 0, 0, 1]], dtype=float)
    b = np.array([10, 8, 6], dtype=float)
    return c, A, b, [3, 4, 5]


if __name__ == "__main__":
    for key, value in initial_simplex_dictionary(*example_data()).items():
        print(f"{key}: {value}")
