import itertools
import re
import sys
import unittest
from pathlib import Path

import clingo

ENCODING = Path(__file__).with_name("hitori.lp")
INSTANCE_PATHS = []


def neighbors(p):
    r, c = p
    return {(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)}


def connected(white):
    if not white:
        return False
    todo = [next(iter(white))]
    seen = set(todo)
    while todo:
        fresh = neighbors(todo.pop()) & (white - seen)
        seen.update(fresh)
        todo.extend(fresh)
    return seen == white


def reference(board):
    # Zweite Suche ohne ASP: jede Zelle färben oder ihren Wert reservieren.
    def search(left, black, white, used):
        if not left:
            if connected(white):
                yield frozenset(black)
            return
        p, *left = left
        r, c = p
        keys = {(0, r, board[p]), (1, c, board[p])}
        if not used & keys:
            yield from search(left, black, white | {p}, used | keys)
        if not black & neighbors(p):
            yield from search(left, black | {p}, white, used)

    return set(search(sorted(board), set(), set(), set()))


def solve(facts):
    ctl = clingo.Control(["0", "--warn=none"])
    ctl.load(str(ENCODING))
    ctl.add("base", [], facts)
    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        results = []
        for model in handle:
            atoms = model.symbols(shown=True)
            assert all(a.name == "shaded" and len(a.arguments) == 2 for a in atoms)
            results.append(frozenset(tuple(x.number for x in a.arguments) for a in atoms))
        assert handle.get().exhausted
    assert len(set(results)) == len(results), "Mehrere Answer Sets für dieselbe Färbung"
    return set(results)


def facts_for(board):
    return "\n".join(f"cell({r},{c},{v})." for (r, c), v in board.items())


class HitoriTests(unittest.TestCase):
    def test_single_cell_must_be_white(self):
        self.assertEqual(solve("cell(1,1,8)."), {frozenset()})

    def test_no_white_path_through_black(self):
        facts = "cell(1,1,1). cell(1,2,2). cell(1,3,3)."
        self.assertNotIn(frozenset({(1, 2)}), solve(facts))

    def test_four_identical_values_have_no_solution(self):
        self.assertEqual(solve("cell(1,1,4). cell(1,2,4). cell(1,3,4). cell(1,4,4)."), set())

    def test_exhaustive_small_boards(self):
        for height, width in ((1, 3), (3, 1), (2, 2), (2, 3), (3, 2)):
            cells = list(itertools.product(range(1, height + 1), range(1, width + 1)))
            for values in itertools.product((1, 2), repeat=len(cells)):
                board = dict(zip(cells, values))
                with self.subTest(shape=(height, width), values=values):
                    self.assertEqual(solve(facts_for(board)), reference(board))

    def test_moodle_instances(self):
        if not INSTANCE_PATHS:
            self.skipTest("Keine Moodle-Instanzen angegeben")
        for path in INSTANCE_PATHS:
            with self.subTest(instance=path.name):
                facts = path.read_text(encoding="utf-8")
                board = {(int(r), int(c)): int(v) for r, c, v in
                         re.findall(r"cell\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\.", facts)}
                expected = reference(board)
                self.assertTrue(expected)
                actual = solve(facts)
                self.assertEqual(actual, expected)
                print(f"{path.name}: {len(actual)} Answer Set(s)", flush=True)


if __name__ == "__main__":
    INSTANCE_PATHS = [Path(arg) for arg in sys.argv[1:]]
    unittest.main(argv=sys.argv[:1], verbosity=2)
